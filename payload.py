import time
from typing import List
from PIL import Image

import formatting
import imagedisplay
from printer import Printer

## payload classes

# base class
# A payload is an abstraction layer for *something* you can do with ANSI injection. 
# There is usually 1 payload per command, but sometimes multiple commands share the same payload (if the logic is similar enough)
class Payload:
    # this function will be called continiously, in here you will do your shenanigans
    def tick(self, printer: Printer): pass

    # notifies when this payload considers itself "done", is used in the `wait` command
    def is_done(self) -> bool:
        return False

# prints the raw byte sequence directly to the console
# if the delay is not None, it will repeat every `delay` milliseconds
class RawPayload(Payload):
    def __init__(self, payload: bytes, delay: int | None = None) -> None:
        super().__init__()
        self.last_print = 0
        self.payload = payload
        self.delay = delay

    def tick(self, printer):
        # make sure it only gets executed once if we want that
        if self.delay == None and self.last_print != 0: return
        # wait `delay` milliseconds
        elif self.delay != None and time.time() * 1000 - self.last_print > self.delay: return

        # try to restore the screen to its original state
        printer.print(self.payload)

        self.last_print = time.time() * 1000
    
    def is_done(self):
        # we are "done" if we are not supposed to loop anymore
        return self.delay == None and self.last_print != 0

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
    
    def is_done(self) -> bool:
        # we are done if we are done with sending the message
        return self.repeat_every == 0 and self.last_print != 0

# prints an image to the screen
class ImagePayload(Payload):
    def __init__(self, display: imagedisplay.ImageDisplay, images: List[Image.Image], delay: int | None = None, clean_mode: str | None = None) -> None:
        self.display = display
        self.did_print = False
        self.images = [display.convert(image) for image in images]
        self.delay = delay
        self.last_print = 0
        self.i = 0

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
    
    def tick(self, printer: Printer):
        if self.delay == None and self.last_print != 0: return
        elif self.delay != None and time.time() * 1000 - self.last_print < self.delay: return

        img = self.images[self.i % len(self.images)]

        printer.print(self.prefix + img + self.stuffix)
        self.last_print = time.time() * 1000
        self.i += 1
    
    def is_done(self) -> bool:
        # if we did 1 full loop we are done
        return self.i >= len(self.images)

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