import math
import sys
from typing import Any, List
import pygame


class Visualizer:
    """Provides graphical simulation interface tracking drones."""

    def __init__(self, graph: Any) -> None:
        """Initializes system visualizer component frameworks."""
        pygame.init()

        self.graph: Any = graph
        self.offset_x: int = 0
        self.offset_y: int = 0

        info = pygame.display.Info()

        self.screen = pygame.display.set_mode(
            (
                info.current_w,
                info.current_h
            )
        )

        self.center_x: int = 50
        self.center_y: int = (
            self.screen.get_height() // 2
        )

        self.tile_size: int = 200

        self.colors = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "orange": (255, 165, 0),
            "magenta": (255, 0, 255),
            "purple": (128, 0, 128),
            "gold": (255, 215, 0),
            "darkred": (139, 0, 0),
            "violet": (148, 0, 211),
            "lime": (0, 255, 0),
            "yellow": (255, 255, 0),
            "brown": (139, 69, 19),
            "black": (0, 0, 0),
            "cyan": (0, 255, 255),
            "maroon": (128, 0, 0),
            "green": (0, 128, 0),
            "crimson": (220, 20, 60),
        }

        self.font = pygame.font.SysFont(
            "",
            30
        )

        self.conn_font = pygame.font.SysFont(
            "",
            18
        )

        self.drones_list: List[Any] = []
        self.simulator: Any = None
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(
            "Fly In"
        )

    def hub_screen_position(self, hub: Any) -> tuple[int, int]:
        """Calculates dynamic viewport matrix translations."""
        x = (
            hub.coordinates[0]
            * self.tile_size
            + self.center_x
            - self.offset_x
        )

        y = (
            hub.coordinates[1]
            * self.tile_size
            + self.center_y
            - self.offset_y
        )

        return int(x), int(y)

    def update(self) -> None:
        """Processes events and updates frames."""
        mouse_x, mouse_y = (
            pygame.mouse.get_pos()
        )

        hovered_hub = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                    if (
                        hasattr(self.graph, 'simulator_instance')
                        and self.graph.simulator_instance
                    ):
                        self.graph.simulator_instance.step_turn()
                    elif self.simulator:
                        self.simulator.step_turn()

        self.screen.fill(
            (60, 60, 60)
        )

        for conn in self.graph.connections_list:
            hub_u = self.graph.hubs[conn.hub_u]
            hub_v = self.graph.hubs[conn.hub_v]

            x1, y1 = self.hub_screen_position(hub_u)
            x2, y2 = self.hub_screen_position(hub_v)

            pygame.draw.line(
                self.screen,
                (200, 200, 200),
                (x1, y1),
                (x2, y2),
                3
            )

            middle_x = (x1 + x2) // 2
            middle_y = (y1 + y2) // 2

            text = self.conn_font.render(
                str(conn.name_of_connection()),
                True,
                (255, 255, 255)
            )

            text_rect = text.get_rect(
                center=(
                    middle_x,
                    middle_y - 15
                )
            )

            self.screen.blit(text, text_rect)

        for hub in self.graph.hubs.values():
            screen_x, screen_y = (
                self.hub_screen_position(hub)
            )

            color = self.colors.get(
                hub.color,
                (255, 255, 255)
            )

            pygame.draw.circle(
                self.screen,
                color,
                (screen_x, screen_y),
                25
            )

            pygame.draw.circle(
                self.screen,
                (0, 0, 0),
                (screen_x, screen_y),
                25,
                2
            )

            if (
                (mouse_x - screen_x) ** 2
                +
                (mouse_y - screen_y) ** 2
            ) <= 25 ** 2:
                hovered_hub = hub

        self.draw_drones()

        if hovered_hub:
            text = self.font.render(
                hovered_hub.name,
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                text,
                (
                    mouse_x + 10,
                    mouse_y - 30
                )
            )

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.offset_x += 5
        if keys[pygame.K_a]:
            self.offset_x -= 5
        if keys[pygame.K_w]:
            self.offset_y -= 5
        if keys[pygame.K_s]:
            self.offset_y += 5

        pygame.display.flip()
        self.clock.tick(60)

    def draw_drones(self) -> None:
        """Renders simulation active drones overlay."""
        position_counts: dict[tuple[int, int], int] = {}

        for drone in self.drones_list:
            current_hub = drone.current_hub()
            next_hub = drone.next_hub()

            if (
                drone.in_flight
                and next_hub
                and next_hub.type_zone == "restricted"
            ):
                x_start, y_start = self.hub_screen_position(current_hub)
                x_end, y_end = self.hub_screen_position(next_hub)

                if drone.turns_left >= 1:
                    base_x = int(x_start + (x_end - x_start) * 0.5)
                    base_y = int(y_start + (y_end - y_start) * 0.5)
                else:
                    base_x, base_y = self.hub_screen_position(next_hub)
            else:
                base_x, base_y = self.hub_screen_position(current_hub)

            pos_key = (base_x, base_y)
            if pos_key not in position_counts:
                position_counts[pos_key] = 0

            drone_index = position_counts[pos_key]
            position_counts[pos_key] += 1

            offset_multiplier = 20

            if drone_index == 0:
                drone_x = base_x
                drone_y = base_y
            else:
                angle = drone_index * (2 * math.pi / 5)
                drone_x = base_x + int(offset_multiplier * math.cos(angle))
                drone_y = base_y + int(offset_multiplier * math.sin(angle))

            pygame.draw.circle(
                self.screen,
                (30, 30, 30),
                (drone_x, drone_y),
                12
            )

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (drone_x, drone_y),
                12,
                2
            )

            drone_id_text = self.conn_font.render(
                f"D{drone.id}",
                True,
                (255, 255, 255)
            )

            drone_id_rect = drone_id_text.get_rect(
                center=(drone_x, drone_y)
            )

            self.screen.blit(
                drone_id_text,
                drone_id_rect
            )
