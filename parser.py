from typing import Dict, Tuple, Set
from hub import Hub
from connection import Connection


class ParseError(ValueError):
    """Exception raised for syntax errors in the map configuration file."""

    def __init__(
        self, message: str, line_number: int, raw_line: str
    ) -> None:
        """Initializes a specific configuration file parsing error."""
        self.message = message
        self.line_number = line_number
        self.raw_line = raw_line

        super().__init__(
            f"Parser Error (Line {self.line_number}): "
            f"{self.message} -> Offending text: '{self.raw_line}'"
        )


class MapParser:
    """Parses, validates, and stores structural network configurations."""

    def __init__(self) -> None:
        """Initializes state variables and strict parsing sets."""
        self.drone_count: int = 0
        self.start_zone: str = ""
        self.end_zone: str = ""
        self.hubs: Dict[str, Hub] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}
        self._coord_to_zone: Dict[Tuple[int, int], str] = {}
        self._valid_zone_types: Set[str] = {
            "normal", "restricted", "blocked", "priority"
        }
        self._allowed_hub_keys: Set[str] = {"zone", "color", "max_drones"}
        self._allowed_conn_keys: Set[str] = {"max_link_capacity"}

    def parse_file(self, file_path: str) -> None:
        """Reads file line-by-line and triggers context parsing workflows."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_num, raw_line in enumerate(file, start=1):
                    line = raw_line.split("#")[0].strip()
                    if not line:
                        continue

                    if self.drone_count == 0:
                        if not line.startswith("nb_drones:"):
                            raise ParseError(
                                "The first structural instruction in the "
                                "configuration file must be 'nb_drones:'.",
                                line_num,
                                raw_line,
                            )

                    if line.startswith("nb_drones:"):
                        self._parse_drone_count(line, line_num, raw_line)
                    elif line.startswith("start_hub:"):
                        self._parse_hub(
                            line, line_num, raw_line, is_start=True
                        )
                    elif line.startswith("end_hub:"):
                        self._parse_hub(line, line_num, raw_line, is_end=True)
                    elif line.startswith("hub:"):
                        self._parse_hub(line, line_num, raw_line)
                    elif line.startswith("connection:"):
                        self._parse_connection(line, line_num, raw_line)
                    else:
                        raise ParseError(
                            "Unknown line prefix rule matching layout schema.",
                            line_num,
                            raw_line,
                        )

            self._verify_map_bounds()

        except FileNotFoundError:
            print(f"Error: The file at '{file_path}' was not found.")
            return

    def _parse_drone_count(
        self, line: str, line_num: int, raw_line: str
    ) -> None:
        """Extracts and validates global initial drone integers."""
        if self.drone_count > 0:
            raise ParseError(
                "Duplicate global initialization of 'nb_drones' detected.",
                line_num,
                raw_line,
            )

        tokens = line.split(":", 1)
        value_string = tokens[1].strip()

        if not value_string:
            raise ParseError(
                "nb_drones parameter value cannot be empty.",
                line_num,
                raw_line,
            )

        try:
            count_integer = int(value_string)
            if count_integer <= 0:
                raise ValueError()
            self.drone_count = count_integer
        except ValueError:
            raise ParseError(
                "nb_drones must specify a valid positive integer.",
                line_num,
                raw_line,
            )

    def _isolate_metadata(
        self, line: str, line_num: int, raw_line: str
    ) -> Tuple[str, str]:
        """Isolates metadata from the right side, preserving brackets."""
        if line.endswith("]"):
            bracket_idx = line.rfind("[")
            if bracket_idx == -1:
                raise ParseError(
                    "Missing opening metadata bracket '['.",
                    line_num,
                    raw_line,
                )

            core_text = line[:bracket_idx].strip()
            metadata_str = line[bracket_idx:].strip()

            if metadata_str.count("[") != 1 or metadata_str.count("]") != 1:
                raise ParseError(
                    "Improper metadata parameter bracket balancing.",
                    line_num,
                    raw_line,
                )

            return core_text, metadata_str.strip("[] ")

        return line.strip(), ""

    def _parse_hub(
        self,
        line: str,
        line_num: int,
        raw_line: str,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Parses zone declarations, properties, and spatial values."""
        core_text, metadata_payload = self._isolate_metadata(
            line, line_num, raw_line
        )

        tokens = core_text.split()
        if len(tokens) != 4:
            raise ParseError(
                "Zone definition must contain exactly: prefix name X Y.",
                line_num,
                raw_line,
            )

        name = tokens[1]
        if name in self.hubs:
            raise ParseError(
                f"Zone name '{name}' has already been declared.",
                line_num,
                raw_line,
            )

        try:
            x_coord = int(tokens[2])
            y_coord = int(tokens[3])
        except ValueError:
            raise ParseError(
                "Zone coordinates parameters must evaluate to integers.",
                line_num,
                raw_line,
            )

        coords = (x_coord, y_coord)
        if coords in self._coord_to_zone:
            conflicting_zone = self._coord_to_zone[coords]
            raise ParseError(
                f"Spatial Collision Error: Coordinates {coords} were already "
                f"assigned to hub zone '{conflicting_zone}'.",
                line_num,
                raw_line,
            )

        zone_type = "normal"
        max_drones = 1
        color = "none"
        seen_attributes: Set[str] = set()

        if metadata_payload:
            tag_pairs = metadata_payload.split()
            for pair in tag_pairs:
                if "=" not in pair:
                    raise ParseError(
                        f"Malformed tag pair syntax: '{pair}'. "
                        f"Must use key=value format.",
                        line_num,
                        raw_line,
                    )
                parts = pair.split("=")
                if (
                    len(parts) != 2
                    or not parts[0].strip()
                    or not parts[1].strip()
                ):
                    raise ParseError(
                        f"Tag syntax violates key-value constraints: "
                        f"'{pair}'",
                        line_num,
                        raw_line,
                    )

                key = parts[0].strip()
                val = parts[1].strip()

                if key not in self._allowed_hub_keys:
                    allowed_keys = sorted(list(self._allowed_hub_keys))
                    raise ParseError(
                        f"Invalid key: '{key}'. Allowed: {allowed_keys}.",
                        line_num,
                        raw_line,
                    )

                if key in seen_attributes:
                    raise ParseError(
                        f"Duplicate declaration of attribute '{key}' "
                        f"in brackets.",
                        line_num,
                        raw_line,
                    )
                seen_attributes.add(key)

                if key == "zone":
                    if val not in self._valid_zone_types:
                        allowed_types = sorted(list(self._valid_zone_types))
                        raise ParseError(
                            f"Invalid zone type '{val}'. "
                            f"Must be: {allowed_types}.",
                            line_num,
                            raw_line,
                        )
                    zone_type = val
                elif key == "color":
                    color = val
                elif key == "max_drones":
                    try:
                        max_drones = int(val)
                        if max_drones <= 0:
                            raise ValueError()
                    except ValueError:
                        raise ParseError(
                            "max_drones configuration must be "
                            "a positive integer.",
                            line_num,
                            raw_line,
                        )

        if is_start:
            if self.start_zone:
                raise ParseError(
                    "Duplicate definition of start_hub detected.",
                    line_num,
                    raw_line,
                )
            self.start_zone = name
            if "max_drones" not in seen_attributes:
                max_drones = self.drone_count
        elif is_end:
            if self.end_zone:
                raise ParseError(
                    "Duplicate definition of end_hub detected.",
                    line_num,
                    raw_line,
                )
            self.end_zone = name
            max_drones = self.drone_count

        self._coord_to_zone[coords] = name
        self.hubs[name] = Hub(
            name=name,
            coordinates=coords,
            type_zone=zone_type,
            max_drones=max_drones,
            color=color
        )

    def _parse_connection(
        self, line: str, line_num: int, raw_line: str
    ) -> None:
        """Validates bidirectional link edges without checking loops."""
        core_text, metadata_payload = self._isolate_metadata(
            line, line_num, raw_line
        )

        if not core_text.startswith("connection:"):
            raise ParseError(
                "Malformed connection prefix token signature.",
                line_num,
                raw_line,
            )

        payload = core_text.replace("connection:", "").strip()
        nodes = payload.split("-")
        if len(nodes) != 2 or not nodes[0].strip() or not nodes[1].strip():
            raise ParseError(
                "Connection format must follow schema: zone1-zone2",
                line_num,
                raw_line,
            )

        zone_u = nodes[0].strip()
        zone_v = nodes[1].strip()

        if zone_u not in self.hubs or zone_v not in self.hubs:
            raise ParseError(
                f"Linkage error: '{zone_u}' and '{zone_v}' must exist first.",
                line_num,
                raw_line,
            )
        if zone_u == zone_v:
            raise ParseError(
                f"Reflexive link error: hub '{zone_u}' "
                f"cannot link to itself.",
                line_num,
                raw_line,
            )

        if zone_u < zone_v:
            normalized_link = (zone_u, zone_v)
        else:
            normalized_link = (zone_v, zone_u)

        if normalized_link in self.connections:
            raise ParseError(
                f"Duplicate connection between '{zone_u}' and '{zone_v}'.",
                line_num,
                raw_line,
            )

        max_link_capacity = 1
        seen_attributes: Set[str] = set()

        if metadata_payload:
            tag_pairs = metadata_payload.split()
            for pair in tag_pairs:
                if "=" not in pair:
                    raise ParseError(
                        f"Malformed connection tag mapping: '{pair}'",
                        line_num,
                        raw_line,
                    )
                parts = pair.split("=")
                if (
                    len(parts) != 2
                    or not parts[0].strip()
                    or not parts[1].strip()
                ):
                    raise ParseError(
                        f"Connection tag violates assignments: '{pair}'",
                        line_num,
                        raw_line,
                    )

                key = parts[0].strip()
                val = parts[1].strip()

                if key not in self._allowed_conn_keys:
                    allowed_keys = sorted(list(self._allowed_conn_keys))
                    raise ParseError(
                        f"Invalid connection key: '{key}'. "
                        f"Allowed: {allowed_keys}.",
                        line_num,
                        raw_line,
                    )

                if key in seen_attributes:
                    raise ParseError(
                        f"Syntax Error: Duplicate connection attribute "
                        f"'{key}' detected.",
                        line_num,
                        raw_line,
                    )
                seen_attributes.add(key)

                if key == "max_link_capacity":
                    try:
                        max_link_capacity = int(val)
                        if max_link_capacity <= 0:
                            raise ValueError()
                    except ValueError:
                        raise ParseError(
                            "max_link_capacity must be a positive integer.",
                            line_num,
                            raw_line,
                        )

        self.connections[normalized_link] = Connection(
            hub_u=zone_u,
            hub_v=zone_v,
            max_link_capacity=max_link_capacity
        )

    def _verify_map_bounds(self) -> None:
        """Validates structural boundary assignments after loop resolution."""
        if not self.start_zone:
            raise ParseError(
                "Map missing a unique start_hub definition.",
                0,
                "EOF Verification Boundary Check"
            )
        if not self.end_zone:
            raise ParseError(
                "Map missing a unique end_hub definition.",
                0,
                "EOF Verification Boundary Check"
            )
