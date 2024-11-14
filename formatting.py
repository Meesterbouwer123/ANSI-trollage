## ANSI codes
BELL = b"\x07"
ANSI_ESC = b"\x1b"
ANSI_OSC = ANSI_ESC + b"]"
ANSI_ST = ANSI_ESC + b"\\"
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
COLORS = [
    BLACK,
    RED,
    GREEN,
    YELLOW,
    BLUE,
    MAGENTA,
    CYAN,
    WHITE,
]

# Proprietary Escape Codes
OSC8_LINK_END = ANSI_OSC + b"8;;" + ANSI_ST

## utility functions
formatting_codes = {
    # colors
    "black": BLACK,
    "red": RED,
    "green": GREEN,
    "yellow": YELLOW,
    "blue": BLUE,
    "magenta": MAGENTA,
    "cyan": CYAN,
    "white": WHITE,
    "default_color": DEFAULT,
    # other ansi codes
    "bell": BELL,
    "wipe": RESET_CONSOLE,
    "hide": ENTER_INVISIBLE_MODE,
    "nohide": EXIT_INVISIBLE_MODE,
    "reset": RESET,
    # extensions
    "nolink": OSC8_LINK_END,

    # not ANSI, but may still be useful
    "crlf": b"\r\n"
}

def parse_text(input: str) -> bytes:
    result = b''
    escaped = False
    i = 0

    while i < len(input):
        c = input[i]

        if escaped:
            if c == '\\' or c == '(':
                # backslash before = print raw
                result += c.encode()
            else:
                raise Exception('invalid escape character \'' + c + '\' at index ' + i)
            
            escaped = False
            i+=1
            continue

        if c == '\\':
            escaped = True
            i+=1
            continue
        
        elif c == '(':
            # we got an opening brace, let's add the format sting instead of the real text

            # get format string
            format_len = input[i:].find(')')
            if format_len == -1: raise Exception('unmatched opening brace at index ' + str(i))
            format = input[i+1:i+format_len]

            # look up the corresponding format code
            if format.lower() in formatting_codes:
                result += formatting_codes[format.lower()]
            elif format.startswith("link "):
                link = format.removeprefix("link ")
                result += start_link(link)
            else:
                raise Exception('unknown format string at index ' + str(i))

            # skip to after the closing brace
            i += format_len + 1
            continue

        result += c.encode()
        i+=1
    
    if escaped:
        raise Exception('you are not supposed to end with a backslash!')
    
    return result

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

def start_link(url: str | bytes):
    if type(url) == str:
        url = url.encode()
    return ANSI_OSC + b"8;;" + url + ANSI_ST

def format_link(url: str | bytes, text: bytes):
    return start_link(url) + text + OSC8_LINK_END