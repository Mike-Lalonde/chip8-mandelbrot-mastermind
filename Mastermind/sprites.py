import random

import pygame
from settings import *


class Pin:
    def __init__(self, x, y, colour=None, revealed=True):
        self.x, self.y = x, y
        self.colour = colour
        self.revealed = revealed

    def draw(self, screen):
        center = (self.x + (TILESIZE/2), self.y + (TILESIZE/2))
        if self.colour is not None and self.revealed:
            pygame.draw.circle(screen, tuple(x * 0.3 for x in self.colour), tuple(x + 1 for x in center), 15)
            pygame.draw.circle(screen, self.colour, center, 15)
        elif not self.revealed:
            pygame.draw.circle(screen, LIGHTGREY, center, 15)
            pygame.draw.circle(screen, BLACK, center, 15, 3)

        else:
            pygame.draw.circle(screen, DARKBROWN, center, 10)


class CluePin(Pin):
    def draw(self, screen):
        center = (self.x + (TILESIZE / 2.5), self.y + (TILESIZE / 2.5))
        if self.colour is not None:
            pygame.draw.circle(screen, self.colour, center, 6)
        else:
            pygame.draw.circle(screen, DARKBROWN, center, 5)


class Board:
    def __init__(self):
        self.tries = 10
        self.pins_surface = pygame.Surface((4*TILESIZE, 11*TILESIZE))
        self.pins_surface.fill(BGCOLOUR)

        self.clue_surface = pygame.Surface((TILESIZE, 11*TILESIZE))
        self.clue_surface.fill(BGCOLOUR)

        self.colour_selection_surface = pygame.Surface((4*TILESIZE, 2*TILESIZE))
        self.colour_selection_surface.fill(LIGHTGREY)

        self.colour_selection = []
        self.board_pins = []
        self.board_clues = []

        self.create_selection_pins()
        self.create_pins()
        self.create_clues()
        self.create_code()

    def create_clues(self):
        for i in range(1, 11):
            temp_row = []
            for row in range(2):
                for col in range(2):
                    temp_row.append(CluePin(col * (TILESIZE//4), (row * (TILESIZE//4)) + i * TILESIZE))
            self.board_clues.append(temp_row)

    def create_pins(self):
        for row in range(11):
            temp_row = []
            for col in range(4):
                temp_row.append(Pin(col * TILESIZE, row * TILESIZE))
            self.board_pins.append(temp_row)

    def create_selection_pins(self):
        colour_index = 0
        for y in range(2):
            for x in range(4):
                if colour_index < AMOUNT_COLOUR:
                    self.colour_selection.append(Pin(x*TILESIZE, y*TILESIZE, COLOURS[colour_index]))
                    colour_index += 1
                else:
                    break

    def draw(self, screen):
        # draw the placeholder for the coloured pins
        for pin in self.colour_selection:
            pin.draw(self.colour_selection_surface)

        # draw the pins
        for row in self.board_pins:
            for pin in row:
                pin.draw(self.pins_surface)

        # draw clue pins
        for row in self.board_clues:
            for pin in row:
                pin.draw(self.clue_surface)

        screen.blit(self.pins_surface, (0, 0))
        screen.blit(self.clue_surface, (4*TILESIZE, 0))
        screen.blit(self.colour_selection_surface, (0, 11*TILESIZE))

        # draw row indicator
        pygame.draw.rect(screen, GREEN, (0, TILESIZE*self.tries, 4*TILESIZE, TILESIZE), 2)

        for x in range(0, WIDTH, TILESIZE):
            for y in range(0, HEIGHT, TILESIZE):
                pygame.draw.line(screen, LIGHTGREY, (x, 0), (x, HEIGHT))
                pygame.draw.line(screen, LIGHTGREY, (0, y), (WIDTH, y))

    def select_colour(self, mx, my, previous_colour):
        for pin in self.colour_selection:
            if pin.x < mx < pin.x + TILESIZE and pin.y < my - 11*TILESIZE < pin.y + TILESIZE:
                return pin.colour

        return previous_colour

    def place_pin(self, mx, my, colour):
        for pin in self.board_pins[self.tries]:
            if pin.x < mx < pin.x + TILESIZE and pin.y < my < pin.y + TILESIZE:
                pin.colour = colour
                break

    def check_row(self):
        return all(pin.colour is not None for pin in self.board_pins[self.tries])
        # for pin in self.board_pins[self.tries]:
        #     if pin.colour is None:
        #         return False
        # return True

    def check_clues(self):
        colour_list = []
        for i, code_pin in enumerate(self.board_pins[0]):
            colour = None
            for j, user_pin in enumerate(self.board_pins[self.tries]):
                if user_pin.colour == code_pin.colour:
                    colour = WHITE
                    if i == j:
                        colour = RED
                        break
            if colour is not None:
                colour_list.append(colour)

        colour_list.sort()
        return colour_list

    def set_clues(self, colour_list):
        for colour, pin in zip(colour_list, self.board_clues[self.tries-1]):
            pin.colour = colour

    def create_code(self):
        # generate ramdon code
        random_code = random.sample(COLOURS, 4)
        for i, pin in enumerate(self.board_pins[0]):
            pin.colour = random_code[i]
            pin.revealed = False
        print(random_code)

    def next_round(self):
        self.tries -= 1
        return self.tries > 0

    def reveal_code(self):
        for pin in self.board_pins[0]:
            pin.revealed = True
