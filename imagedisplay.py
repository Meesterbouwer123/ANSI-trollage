from PIL import Image

class ImageDisplay:
    def __init__(self, w, h, priority) -> None:
        self.w, self.h = w, h
        self.priority = priority
    
    def resize (self, image: Image) -> Image:
        width, height = image.size
        if self.priority == "width":
            return image.resize((self.w, int((height / width) * self.w)))
        elif self.priority == "height":
            return image.resize((int((width / height) * self.h), self.h))
        else:
            return image.resize((self.w, self.h))
        
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
        image = self.resize(image)
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
    return (pixel[0] + pixel[1] + pixel[2])/3