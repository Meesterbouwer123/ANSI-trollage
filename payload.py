import time
import formatting
from printer import Printer

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
        printer.print(formatting.EXIT_INVISIBLE_MODE + formatting.OSC8_LINK_END + formatting.RESET)

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
        printer.print(formatting.RESET_CONSOLE)

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
        printer.print(formatting.BELL)

# broad text display payload, is very versatile
# repeats every `repeat_every` milliseconds, or doesn't repeat if it is 0
# the clean mode can be any one of clean, hide, wipe or none
# the rgb mode can be one of blink, gradient or none
# in case of a gradient RGB the band_size also needs to be specified
class TextDisplay(Payload):
    def __init__(self, payload: bytes, repeat_every: int = 0, clean_mode: str | None = None, rgb_mode: str | None = None, band_size: int = 0) -> None:
        super().__init__()
        self.payload = payload
        self.last_print = 0
        self.i = 0
        self.repeat_every = repeat_every
        self.prefix, self.stuffix = b'', b''

        # parse clean mode
        if clean_mode == "clean":
            self.prefix += formatting.RESET_CURSOR + formatting.EREASE_SCREEN
        elif clean_mode == "hide":
            self.prefix += formatting.EXIT_INVISIBLE_MODE + formatting.RESET_CURSOR + formatting.EREASE_SCREEN
            self.stuffix += formatting.ENTER_INVISIBLE_MODE + formatting.RESET
        elif clean_mode == "wipe":
            self.prefix += formatting.RESET_CONSOLE
        elif clean_mode != None:
            raise Exception("invlaid clean mode, please choose between clean, hide, wipe and none")
        
        # validate rgb mode
        if rgb_mode not in [None, "blink", "gradient"]:
            raise Exception("invlaid rgb mode, please choose between blink, gradient and none")
        self.rgb_mode = rgb_mode
        self.band_size = band_size

    def tick(self, printer):
        # if we don't care about repeating we only print once
        if self.repeat_every == 0 and self.last_print != 0: return
        # if we got called too soon, return
        elif time.time() * 1000 - self.last_print < self.repeat_every: return

        # apply GRB if nessacary
        payload = self.payload
        if self.rgb_mode == "blink":
            code = formatting.COLORS[self.i % len(formatting.COLORS)]
            payload = code + payload + formatting.RESET

        elif self.rgb_mode == "gradient":
            payload = b'\n'.join(rgb_gradient(payload.split(b'\n'), formatting.COLORS, self.i, self.band_size))
            

        # print the text to the console
        printer.print(self.prefix + payload + self.stuffix)
        self.last_print = time.time() * 1000 # store it in milliseconds
        self.i += 1

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
        printer.print(self.color + self.payload + formatting.RESET)

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
        printer.print(formatting.RESET_CURSOR + formatting.EXIT_INVISIBLE_MODE + formatting.EREASE_SCREEN + self.color +  self.payload + formatting.RESET + formatting.ENTER_INVISIBLE_MODE)

# print the text to the console, this will wipe the entire screen and hide everything after the text
class PrintRainbowText(Payload):
    def __init__(self, payload, speed) -> None:
        super().__init__()
        self.payload = payload
        self.speed = speed
        self.last_print_time = 0
        self.i = 0

    def tick(self, printer):
        # only print once every X millis
        current_time = time.time() * 1000
        if current_time < self.last_print_time + self.speed: return
        self.last_print_time = current_time

        # calculate next color
        color = formatting.COLORS[self.i]
        self.i = (self.i + 1) % len(formatting.COLORS)

        # print the text to the console
        printer.print(formatting.RESET_CURSOR + formatting.EXIT_INVISIBLE_MODE + formatting.EREASE_SCREEN + color + self.payload + formatting.RESET + formatting.ENTER_INVISIBLE_MODE)

# prints multiple lines of text with a RGB gradient to the console, this will wipe the entire screen and hide everything after the text
class PrintRGBText(Payload):
    def __init__(self, lines, speed, band_size) -> None:
        super().__init__()
        self.lines = lines
        self.speed = speed
        self.band_size = band_size
        self.last_print_time = 0
        self.i = 0

    def tick(self, printer):
        # only print once every X millis
        current_time = time.time() * 1000
        if current_time < self.last_print_time + self.speed: return
        self.last_print_time = current_time

        # calculate next color
        colored_lines = rgb_gradient(self.lines, formatting.COLORS, self.i, self.band_size)
        self.i += 1
        self.i %= self.band_size * len(formatting.COLORS)

        # print the text to the console
        printer.print(formatting.RESET_CURSOR + formatting.EXIT_INVISIBLE_MODE + formatting.EREASE_SCREEN + b"\n".join(colored_lines) + formatting.ENTER_INVISIBLE_MODE)


## utility functions

# ugly code ahead, i hope to never have to debug this again
def rgb_gradient(text: list[bytes], colors, i: int, band_size: int) -> list[bytes]:
    result = []
    for line in text:
        # calculate where we need to start with the colors
        current_color_index = i // band_size % len(colors)
        line_index = i % band_size
        new_line = colors[current_color_index] + line[:line_index]
        while len(line[line_index:]) > 0:
            current_color_index -= 1
            if current_color_index < 0: current_color_index = len(colors) - 1
            new_line += colors[current_color_index] + line[line_index:line_index+band_size]
            line_index += band_size
        result.append(new_line + formatting.RESET)

        i = (i + 1) % (band_size * len(colors))
    return result