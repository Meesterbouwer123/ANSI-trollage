import sys
import threading
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
    
    elif mode == "self":
        return printer.SelfPrinter()
    
    else:
        return None

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
            if command == "help":
                # i hate python with its bytes
                print(f"{RED.decode()}Commands:{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}help {BLUE.decode()}: {CYAN.decode()}Shows the help for all the commands, you already figured this one out :D{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}stop {BLUE.decode()}: {CYAN.decode()}Stops the currently running payload{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}exit {BLUE.decode()}: {CYAN.decode()}Stops the currently running payload and exits the program{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}reset {BLUE.decode()}: {CYAN.decode()}Tries to recover the console from all the previous shenanigans{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}wipe [permanent] {BLUE.decode()}: {CYAN.decode()}Wipes the console and all the previous content on it, if permanent is selected it will keep wiping the console{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}bell [loop <delay>] {BLUE.decode()}: {CYAN.decode()}Plays an annoying bell sound if the terminal supports it, optionally loops every <delay> milliseconds{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}text [OPTIONS] <text> {BLUE.decode()}: {CYAN.decode()}Displays some text to the console\n  {BLUE.decode()}Using the options you can make the text big (--figlet_font), make the text be the only thing being displayed (--clean_mode and --repeat) or give it RGB colors (--rgb_mode){RESET.decode()}")
                
            elif command == "exit":
                print("Shutting down...")
                running = False
                run_thread.join()
            
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
                    print("Usage: wipe [permanent]")
                    continue

                current_payload = payload.RawPayload(formatting.RESET_CONSOLE, delay=delay)
            
            elif command == "bell" or command.startswith("bell "):
                split = command.split(" ")
                if len(split) == 1:
                    delay = None
                elif split[1] == "loop" and len(split) == 3:
                    try:
                        delay = int(split[2])
                    except:
                        print("Error: the delay must be a number!")
                        continue
                else:
                    print("Usage: bell [loop <delay>]")
                    continue
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
                        error_message = "Please specify a text, not only arguments"
                        break

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
                    print("Error while parsing arguments: " + error_message)
                    continue
                elif band_size == 0 and rgb == "gradient":
                    print("the gradient needs a band size, specified by --gradient_size")
                    continue
                elif band_size != 0 and rgb != "gradient":
                    print("the --band_size needs to be used in combination with --rgb_mode=gradient")
                    continue

                # format the text
                try:
                    formatted = formatting.parse_text(command[i:].strip(), font=font, allow_color=allow_color)
                except Exception as e:
                    print("Error while parsing text: " + e.args[0])
                    continue

                current_payload = payload.TextDisplay(formatted, repeat_every=repeat, clean_mode=clean, rgb_mode=rgb, band_size=band_size)

            elif command.startswith("img "):
                split = command.split(" ")
                i = 1
                if split[1] == "braille":
                    try:
                        width, height = int(split[2]), int(split[3])
                    except:
                        print("The width and height need to be numbers!")
                        continue
                    priority = split[4]
                    if priority not in ["width", "height", "resize"]:
                        print("Invalid priority, choose between width, heigth or resize")
                        continue
                    display = imagedisplay.BrailleDisplay(width, height, priority)
                    i = 4
                else:
                    print("Unknown image mode")
                    continue

                try:
                    p = payload.ImagePayload(display, " ".join(split[i+1:]))
                except Exception as e:
                    print(str(e))
                    continue
                current_payload = p

            elif command == "": pass

            else:
                print("Unknown command '%s'" % command)

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