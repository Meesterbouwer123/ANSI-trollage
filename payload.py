import time

from printer import Printer

## ANSI codes
BELL = b"\x07"
ANSI_ESC = b"\x1b"
RESET = ANSI_ESC + b"[0m"
EREASE_SCREEN = ANSI_ESC + b"[2J"
ENTER_INVISIBLE_MODE = ANSI_ESC + b"[8m"
EXIT_INVISIBLE_MODE = ANSI_ESC + b"[28m"
RESET_CURSOR = ANSI_ESC + b"[H"
RESET_CONSOLE = ANSI_ESC + b"c"

# color codes
BLACK = ANSI_ESC + b"[30m"
RED = ANSI_ESC + b"[31m"
GREEN = ANSI_ESC + b"[32m"
YELLOW = ANSI_ESC + b"[33m"
BLUE = ANSI_ESC + b"[34m"
MAGENTA = ANSI_ESC + b"[35m"
CYAN = ANSI_ESC + b"[36m"
WHITE = ANSI_ESC + b"[37m"
DEFAULT = ANSI_ESC + b"[39m"

## payload classes

# base class
class Payload:
    # this function will be called continiously, in here you will do your shenanigans
    def tick(self, printer: Printer): pass

# tries to recover the console from previous shenanigans
class Reset(Payload):
    def __init__(self) -> None:
        super().__init__()
        self.did_print_already = False

    def tick(self, printer):
        # make sure it only gets executed once
        if self.did_print_already: return
        self.did_print_already = True

        # try to restore the screen to its original state
        printer.print(EXIT_INVISIBLE_MODE + RESET)

# wipes the entire screen and the history
class Wipe(Payload):
    def __init__(self, infinite = False) -> None:
        super().__init__()
        self.did_print_already = False
        self.infinite = infinite

    def tick(self, printer):
        # make sure it only gets executed once
        if self.did_print_already and not self.infinite: return
        self.did_print_already = True

        # wipe the entire console
        printer.print(RESET_CONSOLE)

# makes an annoying bell sound
class Bell(Payload):
    def __init__(self, delay = None) -> None:
        super().__init__()
        self.last_print_time = 0
        self.delay = delay

    def tick(self, printer):
        current_time = time.time() * 1000
        
        if self.delay == None: 
            # if we didn't specify a delay, only print once
            if self.last_print_time != 0: return
        
        else:
            # only print once every X millis
            if current_time < self.last_print_time + self.delay: return
        
        self.last_print_time = current_time

        # Make the bell sound
        printer.print(BELL)

# print the text to the console, it will probably be surrounded by other text
class PrintText(Payload):
    def __init__(self, payload) -> None:
        super().__init__()
        self.payload = payload
        self.did_print_already = False

    def tick(self, printer):
        # make sure it only gets executed once
        if self.did_print_already: return
        self.did_print_already = True

        # print the text to the console
        printer.print(self.payload)

# send colored text to the console, this might also be surrounded by other text, but it is more visible
class PrintColoredText(Payload):
    def __init__(self, payload, color) -> None:
        super().__init__()
        self.payload = payload
        self.did_print_already = False
        self.color = color

    def tick(self, printer):
        # make sure it only gets executed once
        if self.did_print_already: return
        self.did_print_already = True

        # print the text to the console
        printer.print(self.color + self.payload + RESET)

# print the text to the console, this will wipe the entire screen and hide everything after the text
class PrintFullscreenText(Payload):
    def __init__(self, payload, color=b"") -> None:
        super().__init__()
        self.payload = payload
        self.did_print_already = False
        self.color = color

    def tick(self, printer):
        # make sure it only gets executed once
        if self.did_print_already: return
        self.did_print_already = True

        # print the text to the console
        printer.print(RESET_CURSOR + EXIT_INVISIBLE_MODE + EREASE_SCREEN + self.color +  self.payload + RESET + ENTER_INVISIBLE_MODE)

# print the text to the console, this will wipe the entire screen and hide everything after the text
class PrintRainbowText(Payload):
    def __init__(self, payload, speed) -> None:
        super().__init__()
        self.payload = payload
        self.speed = speed
        self.last_print_time = 0
        self.i = 0
        self.colors = [
            BLACK,
            RED,
            GREEN,
            YELLOW,
            BLUE,
            MAGENTA,
            CYAN,
            WHITE,
        ]

    def tick(self, printer):
        # only print once every X millis
        current_time = time.time() * 1000
        if current_time < self.last_print_time + self.speed: return
        self.last_print_time = current_time

        # calculate next color
        color = self.colors[self.i]
        self.i = (self.i + 1) % len(self.colors)

        # print the text to the console
        printer.print(RESET_CURSOR + EXIT_INVISIBLE_MODE + EREASE_SCREEN + color + self.payload + RESET + ENTER_INVISIBLE_MODE)

# prints multiple lines of text with a RGB gradient to the console, this will wipe the entire screen and hide everything after the text
class PrintRGBText(Payload):
    def __init__(self, lines, speed, band_size) -> None:
        super().__init__()
        self.lines = lines
        self.speed = speed
        self.band_size = band_size
        self.last_print_time = 0
        self.i = 0
        self.colors = [
            RED,
            YELLOW,
            GREEN,
            BLUE,
            MAGENTA,
            CYAN,
            WHITE,
            BLACK,
        ]

    def tick(self, printer):
        # only print once every X millis
        current_time = time.time() * 1000
        if current_time < self.last_print_time + self.speed: return
        self.last_print_time = current_time

        # calculate next color
        colored_lines = color_text(self.lines, self.colors, self.i, self.band_size)
        self.i += 1
        self.i %= self.band_size * len(self.colors)

        # print the text to the console
        printer.print(RESET_CURSOR + EXIT_INVISIBLE_MODE + EREASE_SCREEN + b"\n".join(colored_lines) + ENTER_INVISIBLE_MODE)


## utility functions
def parse_color(c: str):
    c = c.lower()
    if c == "black": return BLACK
    elif c == "red": return RED
    elif c == "green": return GREEN
    elif c == "yellow": return YELLOW
    elif c == "blue": return BLUE
    elif c == "magenta": return MAGENTA
    elif c == "cyan": return CYAN
    elif c == "white": return WHITE
    elif c == "default": return DEFAULT
    else: return RESET

# ugly code ahead, i hope to never have to debug this again
def color_text(text: list[bytes], colors, i: int, band_size: int) -> list[bytes]:
    result = []
    for line in text:
        # calculate where we need to start with the colors
        current_color_index = i // band_size
        line_index = i % band_size
        new_line = colors[current_color_index] + line[:line_index]
        while len(line[line_index:]) > 0:
            current_color_index -= 1
            if current_color_index < 0: current_color_index = len(colors) - 1
            new_line += colors[current_color_index] + line[line_index:line_index+band_size]
            line_index += band_size
        result.append(new_line + RESET)

        i = (i + 1) % (band_size * len(colors))
    return result