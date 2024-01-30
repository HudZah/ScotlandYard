import pygame
import sys
import json
from enum import Enum
import random
import time
from termcolor import colored, cprint  # Added for colored text in terminal


class Color(Enum):
    CYAN = (0, 255, 255, "cyan")
    BLUE = (0, 0, 255, "blue")
    ORANGE = (255, 165, 0, "yellow")
    MAGENTA = (255, 0, 255, "magenta")
    RED = (255, 0, 0, "red")
    BLACK = (0, 0, 0, "grey")


class Player:
    def __init__(self, name, start_point, color):
        self.name = name
        self.position = start_point
        self.color = color
        self.tickets = {
            "taxi": 10,
            "bus": 8,
            "underground": 4,
            "black": 0,
            "double": 0,
        }

    def get_possible_moves(self, nodes):
        possible_moves = []
        if self.position in nodes:
            for ticket_type, neighbours in (
                nodes[self.position].get_neighbours().items()
            ):
                if self.has_ticket(ticket_type):
                    possible_moves.extend(neighbours)
        return possible_moves

    def get_position(self):
        return self.position

    def get_left_tickets(self):
        return self.tickets

    def has_ticket(self, ticket_type):
        return self.tickets[ticket_type] > 0

    def get_num_tickets(self, ticket_type):
        return self.tickets[ticket_type]

    def get_name(self):
        return self.name


class Detective(Player):
    def __init__(self, name, start_point, color, mrX):
        super().__init__(name, start_point, color)
        self.mrX = mrX

    def move(self, new_position, ticket_type):
        self.tickets[ticket_type] -= 1
        self.position = new_position
        # Implemented TODO: increment MrX's tickets
        self.mrX.tickets[ticket_type] += 1


class MrX(Player):
    def __init__(self, name, start_point, color):
        super().__init__(name, start_point, color)
        self.travel_log = []
        self.tickets = {
            "taxi": 4,
            "bus": 3,
            "underground": 3,
            "black": 5,
            "double": 2,
        }
        # self.tickets["double"] = 2 no double for now

    def move(self, new_position, ticket_type):
        self.travel_log.append(new_position)
        self.tickets[ticket_type] -= 1
        self.position = new_position

    def get_travel_log(self):
        return self.travel_log


class Node:
    def __init__(self, number, station_type, black_station):
        self.number = number
        self.station_type = station_type
        self.black_station = black_station
        self.neighbour_taxis = []
        self.neighbour_buses = []
        self.neighbour_undergrounds = []

    def add_neighbour_taxi(self, taxi_number):
        self.neighbour_taxis.append(taxi_number)

    def add_neighbour_bus(self, bus_number):
        self.neighbour_buses.append(bus_number)

    def add_neighbour_underground(self, underground_number):
        self.neighbour_undergrounds.append(underground_number)

    def get_neighbours(self):
        return {
            "taxi": self.neighbour_taxis,
            "bus": self.neighbour_buses,
            "underground": self.neighbour_undergrounds,
        }

    def __repr__(self):
        return f"Node({self.number}, {self.station_type}, {self.black_station})"


class ScotlandYardGame:
    def __init__(self):
        pygame.init()
        self.window_size = (760, 570)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Scotland Yard Game")
        self.map_image = pygame.image.load("data/map.png")
        self.map_rect = self.map_image.get_rect()
        with open("data/stations.json") as f:
            self.stations_data = json.load(f)
        self.gui_positions = {
            station["number"]: (
                station["guiCoordinates"][0],
                station["guiCoordinates"][1],
            )
            for station in self.stations_data
        }
        self.nodes = {
            station["number"]: Node(
                station["number"],
                station["stationType"],
                station["blackStation"],
            )
            for station in self.stations_data
        }
        self.game_over = False
        for station in self.stations_data:
            node = self.nodes[station["number"]]
            for taxi_number in station["neighbourTaxis"]:
                node.add_neighbour_taxi(taxi_number)
            for bus_number in station["neighbourBuses"]:
                node.add_neighbour_bus(bus_number)
            for underground_number in station["neighbourUndergrounds"]:
                node.add_neighbour_underground(underground_number)
        self.start_points = [
            "13",
            "26",
            "29",
            "34",
            "50",
            "53",
            "91",
            "94",
            "103",
            "112",
            "117",
            "132",
            "138",
            "141",
            "155",
            "174",
            "197",
            "198",
        ]
        self.players = []

    def run(self):
        running = True
        font = pygame.font.Font(None, 24)  # Create a font object
        turn_count = 0
        max_turns = 24

        self.initBoard()

        pygame.display.flip()  # Render the game fully before starting the game loop

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.blit(self.map_image, self.map_rect)
            for player in self.players:
                pos = self.gui_positions[player.get_position()]
                pygame.draw.circle(self.screen, player.color.value[:3], pos, 10)
            if turn_count < max_turns and not self.game_over:
                self.turn()
                turn_count += 1

                time.sleep(1)

                turn_text = font.render(
                    f"Turn: {turn_count}/{max_turns}",
                    True,
                    (255, 255, 255),
                )
                self.screen.blit(turn_text, (10, 10))

            pygame.display.flip()

            if self.game_over:
                print(
                    colored(
                        "MrX has been caught! Detectives have won!",
                        "green",
                        attrs=["bold"],
                    )
                )
                time.sleep(5)
                running = False
            elif turn_count >= max_turns:
                print(colored("MrX has won!", "red", attrs=["bold"]))
                time.sleep(5)
                running = False

        pygame.quit()
        sys.exit()

    def initBoard(self):
        # Create MrX
        mrX_start_point = int(random.choice(self.start_points))
        self.mrX = MrX("MrX", mrX_start_point, Color.BLACK)
        self.players.append(self.mrX)

        # Create detectives
        detective_colors = [
            Color.CYAN,
            Color.BLUE,
            Color.ORANGE,
            Color.MAGENTA,
            Color.RED,
        ]
        for i, color in enumerate(detective_colors):
            detective_start_point = int(random.choice(self.start_points))
            detective = Detective(
                f"Detective{i+1}", detective_start_point, color, self.mrX
            )
            self.players.append(detective)

    def turn(self):
        for player in self.players:
            self.current_player = player
            possible_moves = player.get_possible_moves(self.nodes)
            if possible_moves:
                new_position = random.choice(possible_moves)
                random_ticket = random.choice(
                    [
                        ticket
                        for ticket, num in player.get_left_tickets().items()
                        if num > 0
                    ]
                )
                player.move(new_position, random_ticket)
                cprint(
                    f"{player.get_name()} moved to {new_position}. Remaining tickets: {player.get_left_tickets()}\n",
                    player.color.value[3],
                    attrs=["bold"],
                )
                if (
                    isinstance(player, Detective)
                    and player.get_position() == self.mrX.get_position()
                ):
                    cprint("MrX has been caught!\n", "magenta", attrs=["bold"])
                    self.game_over = True
                    break
        print("-" * 50)


if __name__ == "__main__":
    game = ScotlandYardGame()
    game.run()
