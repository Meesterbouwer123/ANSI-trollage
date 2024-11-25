from PIL import Image, ImageSequence

class ImageDisplay:
    def __init__(self, width: int | None, height: int | None) -> None:
        self.w, self.h = width, height
    
    def resize (self, image: Image) -> Image:
        width, height = image.size
        if self.w != None and self.h == None:
            return image.resize((self.w, int((height / width) * self.w)))
        elif self.w == None and self.h != None:
            return image.resize((int((width / height) * self.h), self.h))
        elif self.w != None and self.h != None:
            return image.resize((self.w, self.h))
        else:
            return image # no resizing needed
        
    def convert(self, image: Image) -> bytes:
        pass


class BrailleDisplay(ImageDisplay):
    def braille_char(self, image: Image, x, y) -> str:
        w, h = image.size
        code = 0x2800
        lookup = [
            [0x1, 0x8],
            [0x2, 0x10],
            [0x4, 0x20],
            [0x40, 0x80],
        ]
        for k in range(2*4):
            _x, _y = k//4, k%4
            # if we reach out of bounds, just ignore it
            if x + _x >= w or y + _y >= h: continue

            brightness = grayscale(image, x + _x, y + _y)
            if brightness > 128:
                code |= lookup[_y][_x]
        
        res = chr(code)
        return res

    def convert(self, image: Image) -> bytes:
        image = self.resize(image).convert('1') # this conversion turns the image into black and white, the added dithering makes the images more recognizable
        result = ""
        w, h = image.size
        for y in range(0, h, 4):
            for x in range(0, w, 2):
                # convert to braille character
                result += self.braille_char(image, x, y)
            result += "\n"
        return result.encode()

def grayscale(image, x, y):
    pixel = image.getpixel((x, y))
    if type(pixel) == int: return pixel
    # calculate average
    return (pixel[0] + pixel[1] + pixel[2])/3

def read_images(file: str) -> list[Image.Image]:
    with Image.open(file) as im:
        return ImageSequence.all_frames(im, lambda x: x) # this seems like the easiest function to use, but we need to pass a function to it. we use a stupid lambda for this