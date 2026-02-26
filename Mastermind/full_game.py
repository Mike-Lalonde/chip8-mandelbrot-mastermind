import random
import pygame

# From the Tutorial https://www.youtube.com/watch?v=5GjjX7gNlwI .  
#  I thought this was a cool tutorial and wanted to make it, seeing how we are doing OOP too
# I have incorporated my own changes and additions. 
# My changes:
#  - Adding sound to pygame/python projects https://www.youtube.com/watch?v=3Yhhzflmxfs
#  - Added the "confirm button" <EVENT> to make game completely playable by mouse  https://www.pygame.org/docs/
#    https://www.youtube.com/watch?v=8SzTzvrWaAA  - Clear Code Pygame button logic
#  - Changed visual appearances


# settings.py 

# my chosen colour palette for the game! (r, g, b)
#   I did not use every colour but have left some in for future game mods

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)

DARKGREY = (40, 40, 40)
LIGHTGREY = (120, 80, 80)
DARKBROWN = (55, 22, 30)
GREEN = (0, 210, 0)
NEONGREEN = (57, 255, 20)
BLUE = (0, 0, 200)
SEAFOAM = (33, 225, 246)
RED = (210, 0, 0)
YELLOW = (210, 210, 0)
PALEYELLOW = (110, 110, 10)
PINK = (210, 0, 210)
VIOLET = (127, 0, 255)
ORANGE = (210, 110, 0)
GOLD = (153, 101, 21)
PEARLPINK = (245, 210, 230)

# Mother-of-pearl style background (soft pearly off-white)
BGCOLOUR = (240, 236, 229)


COLOURS = (RED, GREEN, BLUE, YELLOW, PINK, ORANGE, SEAFOAM, VIOLET, BLACK, WHITE)

# This is setting up the board and tiles
ROWS = 5 # this represents how many columns the board will have
COLS = 13 # this represents how many rows the board will have
TILES = 60 #represents the pixels of each tile
AMOUNT_COLOUR = 8 # colours tht can be used to comprise the secret code

WIDTH = (ROWS * TILES) + 1 #the width of the game gui
HEIGHT = (COLS * TILES) + 1 # the length of the game gui
FPS = 60  #game loops frames per second
TITLE = "Mastermind ASSIGN2"  # the little title at the top

# SPRITE.PY
# First object represents a single guess pin
# ENCAPSULATION : 
    # Each Pin stores its own x, y, colour, and revealed state, and has its own draw() method.
    # Nothing else needs to know how a pin draws itself – they just call pin.draw(screen).

class Pin:
 # The constructor method for this class; it runs when you create a Pin()   
    def __init__(self, x, y, colour=None, revealed=True): 
        # store the tile coordinates, colour and hidden status for created pin
        self.x, self.y = x, y 
        self.colour = colour
        self.revealed = revealed
        #function for each pin instance to draw itself
    def draw(self, screen):
         #compute the centre of the pin tile for drawing circles 
        center = (self.x + (TILES / 2), self.y + (TILES / 2))
        # if pin is visible draw a shadow for a 3d effect
        if self.colour is not None and self.revealed:
            pygame.draw.circle(
                screen,
                tuple(c * 0.3 for c in self.colour), #this creates a darker coloured shadow
                tuple(v + 10 for v in center), #moves the shadow
                12,
            )
            # conditions for drawing a pin that isn't revealed...ie the code pins
            pygame.draw.circle(screen, self.colour, center, 15)
        elif not self.revealed:
            pygame.draw.circle(screen, LIGHTGREY, center, 15)
            pygame.draw.circle(screen, LIGHTGREY, center, 15, 3)
        else:
            pygame.draw.circle(screen, DARKBROWN, center, 10)

# CluePin is a type of pin and inherits from Pin BUT it overides the draw feature
# to make them smaller

class CluePin(Pin):

    def draw(self, screen):
        center = (self.x + (TILES / 2.5), self.y + (TILES / 2.5))
        if self.colour is not None:
            pygame.draw.circle(screen, self.colour, center, 6)
        else:
            pygame.draw.circle(screen, PALEYELLOW, center, 5) # pale yellow to offset white clue markers

# Board is an OOP "manager" object: it owns all pins, clue pins, the code, and drawing logic
#  Composition?????? A Board has many Pins and CluePins.”
class Board:
    def __init__(self):
        # How many turns/ attempts before game ends
        self.attempts = 10
        # This is for the play surface
        self.pins_surface = pygame.Surface((4 * TILES, 11 * TILES))
        self.pins_surface.fill(BGCOLOUR)
        # This is the marker pins area
        self.clue_surface = pygame.Surface((TILES, 11 * TILES))
        self.clue_surface.fill(BGCOLOUR)
        # This is the Pint Tray Area
        self.pin_tray = pygame.Surface((4 * TILES, 2 * TILES))
        self.pin_tray.fill(PEARLPINK)
        # These lists hold,  my palette,the guesses and clue pins for each attampt (Top to bottom)
        self.colour_selection = []
        self.board_pins = []
        self.board_clues = []

        # Top to bottom Creates the colour palette, the pins, the cluepins and the secret code for the game
        self.create_selection_pins()
        self.create_pins()
        self.create_clues()
        self.create_code()

      # creates the 2x2 clue pin grid for each guess row
    def create_clues(self):
        for i in range(1, 11):
            temp_row = []
            for row in range(2):
                for col in range(2):
                    temp_row.append(
                        CluePin(
                            col * (TILES // 4),
                            (row * (TILES // 4)) + i * TILES,
                        )
                    )
            self.board_clues.append(temp_row)
    # create the main pins grid (11 rows x 4 columns)
    def create_pins(self):
        for row in range(11):
            temp_row = []
            for col in range(4):
                temp_row.append(Pin(col * TILES, row * TILES))
            self.board_pins.append(temp_row)
    # create the colour selection "palette" pins that the player can click on
    def create_selection_pins(self):
        colour_index = 0
        for y in range(2): #2 rows
            for x in range(4): # 4 columns (2 x 4 = 8 colours)
                if colour_index < AMOUNT_COLOUR:
                    self.colour_selection.append(
                        Pin(x * TILES, y * TILES, COLOURS[colour_index])
                    )
                    colour_index += 1
                else:
                    break
    # draw the entire board (selection tray, pins, clues, grid, and OK button)
    def draw(self, screen):
        # draw the placeholder for the coloured pins
        for pin in self.colour_selection:
            pin.draw(self.pin_tray)

        # draw the pins
        for row in self.board_pins:
            for pin in row:
                pin.draw(self.pins_surface)

        # draw clue pins
        for row in self.board_clues:
            for pin in row:
                pin.draw(self.clue_surface)

        # blit - means to draw something onto something else in the same position
        # for this code specifically, im telling the program to draw the mastermind board,
        # draw the pins in the pin tray and draw over the secret code.

        screen.blit(self.pins_surface, (0, 0))
        screen.blit(self.clue_surface, (4 * TILES, 0))
        screen.blit(self.pin_tray, (0, 11 * TILES))

        # draw row indicator = the light green box 
        pygame.draw.rect(
            screen,
            NEONGREEN,
            (0, TILES * self.attempts, 4 * TILES, TILES),
            4,
        )

        # drawing the grid lines
        for x in range(0, WIDTH, TILES):
            for y in range(0, HEIGHT, TILES):
                pygame.draw.line(screen, LIGHTGREY, (x, 0), (x, HEIGHT))
                pygame.draw.line(screen, LIGHTGREY, (0, y), (WIDTH, y))

        # MY ADD -- draw the "CONFIRM" button in bottom-right tile
        # define the rectangle area
        submit_rect = pygame.Rect(4 * TILES, 12 * TILES, TILES, TILES)
        # draw a PEARLPINK border around the confirm button
        pygame.draw.rect(screen, PEARLPINK, submit_rect, 2)
        # create a font object (None = default font, size 14)
        font = pygame.font.Font(None, 14)
        # render the text "CONFIRM" in GOLD colour
        text = font.render("CONFIRM", True, GOLD)
        # get a rectangle for the text, centred in the submit_rect
        text_rect = text.get_rect(center=submit_rect.center)
        # draw the text onto the screen
        screen.blit(text, text_rect)
    #function that handle selecting a colour from the palette based on mouse click
    def select_colour(self, mx, my, previous_colour):
        for pin in self.colour_selection:
            # if mouse click (mx, my) falls within this pin's tile
            # note: my - 11*TILES adjusts because selection surface is drawn lower on the screen
            if pin.x < mx < pin.x + TILES and pin.y < my - 11 * TILES < pin.y + TILES:
                return pin.colour
        return previous_colour
    # place a pin in the current guess row if click is inside a valid tile
    def place_pin(self, mx, my, colour):
        for pin in self.board_pins[self.attempts]:
            if pin.x < mx < pin.x + TILES and pin.y < my < pin.y + TILES:
                pin.colour = colour
                return True  # successfully placed
        return False  # nothing placed
    # check if every pin in the current guess row has a colour (no None values)
    def check_row(self):
        return all(pin.colour is not None for pin in self.board_pins[self.attempts])

    # Function that computes clue pegs (black and white) for the current guess row
    def check_clues(self):
        code_row = self.board_pins[0]
        guess_row = self.board_pins[self.attempts]

        black = 0
        code_remaining = []
        guess_remaining = []

        # First pass: exact matches (black pins)
        for code_pin, guess_pin in zip(code_row, guess_row):
            if guess_pin.colour == code_pin.colour:
                black += 1
            else:
                code_remaining.append(code_pin.colour)
                guess_remaining.append(guess_pin.colour)

        # Second pass: colour-only matches (white pins)
        white = 0
        code_temp = code_remaining.copy()
        for gc in guess_remaining:
            if gc in code_temp:
                white += 1
                code_temp.remove(gc)

        colour_list = [BLACK] * black + [WHITE] * white
        return colour_list
    # logic for setting the clue pins
    def set_clues(self, colour_list):
        # zip takes two lists and lines them up pair-by-pair, so each clue colour 
        # gets matched with the specific CluePin object it should be applied to.
        for colour, pin in zip(colour_list, self.board_clues[self.attempts - 1]):
            pin.colour = colour

    def create_code(self):
        # generate random code that allows duplicated colours
        available_colours = COLOURS[:AMOUNT_COLOUR]
        random_code = [random.choice(available_colours) for _ in range(4)]
        for i, pin in enumerate(self.board_pins[0]):
            pin.colour = random_code[i]
            pin.revealed = False
        print(random_code)
        # move to the next attempt row
    def next_round(self):
        self.attempts -= 1
        return self.attempts > 0
     # reveal the secret code in the top row at the end of the game
    def reveal_code(self):
         # for each pin in the secret code row
        for pin in self.board_pins[0]:
            # set revealed to True so Pin.draw will show the colour
            pin.revealed = True

# MAIN.PY
# Game is the overall controller class: sets up pygame, owns a Board, and runs the main gaming loop
class Game:
    def __init__(self):
         # initialise all pygame modules
        pygame.init()
        # init audio
        try:
            pygame.mixer.init() # try to initialise mixer for sound playback
        except pygame.error as e:
            print("Audio init failed:", e) # print an error if audio fails but don't crash the game

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # my modification to bring sound into the game
        # snap_sound will be played when a peg is successfully placed
        self.snap_sound = None
        # win_sound will be played when the player wins
        self.win_sound = None
        # lose_sound will be played when the player loses
        self.lose_sound = None

        # try/ excepts for practice AND stability
        try:
            self.snap_sound = pygame.mixer.Sound("click-1117.wav")
        except pygame.error:
            print("Warning: click-1117.wav not found or could not be loaded.")

        try:
            self.win_sound = pygame.mixer.Sound("applause.wav")
        except pygame.error:
            print("Warning: applause.wav not found or could not be loaded.")

        try:
            self.lose_sound = pygame.mixer.Sound("lose_trombone471.wav")
        except pygame.error:
            print("Warning: lose_trombone471.wav not found or could not be loaded.")

 # create a fresh board and reset selected colour
    def new(self):
        # create a new Board instance (OOP composition: Game "has a" Board)
        self.board = Board()
        # no colour selected at the beginning
        self.colour = None

    # main game loop for a single playthrough
    def run(self):
        # flag to keep the loop running
        self.playing = True
        # loop as long as the game is in "playing" state
        while self.playing:
            # limit the loop to FPS frames per second
            self.clock.tick(FPS)
            # handle all user input and events
            self.events()
            # draw the current frame
            self.draw()

    # handle drawing the current state to the screen
    def draw(self):
        # fill the whole screen with the background colour
        self.screen.fill(BGCOLOUR)
        # ask the Board object to draw itself onto the screen
        self.board.draw(self.screen)
        # update the display so we see what was drawn
        pygame.display.flip()

    #  THE EVENTHANDLER mouse, keyboaard, sound and quit
    def events(self):
        # process all events in the event queue
        for event in pygame.event.get():
            # if the window close button was clicked
            if event.type == pygame.QUIT:
                # shut down pygame
                pygame.quit()
                # exit the program
                quit(0)

            # if the left mouse button was pressed
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # get mouse x and y position at time of click
                mx, my = event.pos
                # ask the Board to update currently selected colour if a palette pin was clicked
                self.colour = self.board.select_colour(mx, my, self.colour)

                # place pin in current attempt row
                # if a colour is selected (not None) try to place a peg in the current row
                if self.colour is not None:
                    # attempt to place a pin in the current attempts row based on click position
                    placed = self.board.place_pin(mx, my, self.colour)
                    # if a pin was successfully placed and we have a snap sound loaded
                    if placed and self.snap_sound is not None:
                        # play the snap sound effect
                        self.snap_sound.play()

                # here we check if the click is inside the confirm tile
                if (4 * TILES) <= mx < (5 * TILES) and (12 * TILES) <= my < (13 * TILES):
                    # only submit if the row is fully filled
                    if self.board.check_row():
                        # compute the clue colours for the current guess
                        clues_colour_list = self.board.check_clues()
                        # apply those clue colours to the clue pins
                        self.board.set_clues(clues_colour_list)
                        # if all clues indicate a win
                        if self.check_win(clues_colour_list):
                            # print a win message in the console
                            print("Congrats! You've Won!")
                            # play win sound if available
                            if self.win_sound is not None:
                                self.win_sound.play()
                            # reveal the secret code row
                            self.board.reveal_code()
                            # go to the end screen (wait for Enter to restart)
                            self.end_screen()
                        # if the guess was not correct and there are no attempts left
                        elif not self.board.next_round():
                            # print a lose message in the console
                            print("Tough Luck! Game Over!")
                            # play losing trombone sound if available
                            if self.lose_sound is not None:
                                self.lose_sound.play()
                            # reveal the secret code row
                            self.board.reveal_code()
                            # move to the end screen
                            self.end_screen()

    def check_win(self, colour_list):
        # win condition: exactly 4 clues and all of them are black
        return len(colour_list) == 4 and all(colour == BLACK for colour in colour_list)

    def end_screen(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.playing = False
                    return

            self.draw()


if __name__ == "__main__":
    game = Game()
    while True:
        game.new()
        game.run()
