import pygame
import sys
import json


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
        self.gui_positions = [
            tuple(station["guiCoordinates"]) for station in self.stations_data
        ]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.blit(self.map_image, self.map_rect)
            for pos in self.gui_positions:
                pygame.draw.circle(self.screen, (0, 0, 0), pos, 8, 1)

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ScotlandYardGame()
    game.run()
