import sys
import threading
import pyfiglet
# our own modules
import printer
import payload
from payload import ANSI_OSC, ANSI_ST, OSC8_LINK_END, RED, RESET, CYAN, BLUE

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
    
    else:
        return None

def main():
    global running, current_payload
    
    p = get_printer()
    if p == None:
        print("Usage: %s <printer> [options]" % sys.argv[0])
        print("Available printers:")
        print("- socket <host> <port> : plain old socket connection (aliases: sock, nc, netcat)")
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
                print(f"{RED.decode()}- {CYAN.decode()}help {BLUE.decode()}: {CYAN.decode()}shows the help for all the commands{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}exit {BLUE.decode()}: {CYAN.decode()}Stops the currently running payload and exits the program{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}reset {BLUE.decode()}: {CYAN.decode()}Tries to recover the console from all the previous shenanigans{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}wipe [permanent] {BLUE.decode()}: {CYAN.decode()}Wipes the console and all the previous content on it, if permanent is selected it will keep wiping the console{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}bell [loop <delay>] {BLUE.decode()}: {CYAN.decode()}Plays an annoying bell sound if the terminal supports it, optionally loops every <delay> milliseconds{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}txt <payload> {BLUE.decode()}: {CYAN.decode()}Displays the payload to the target console{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}ctxt <color> <payload> {BLUE.decode()}: {CYAN.decode()}Displays the payload to the target console in the desired color{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}fulltxt <payload> {BLUE.decode()}: {CYAN.decode()}Displays the payload to the target console, wipes everything else{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}cfulltxt <color> <payload> {BLUE.decode()}: {CYAN.decode()}Displays the payload to the target console in the desired color, wipes everything else{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}rgb <delay> <text> {BLUE.decode()}: {CYAN.decode()}Displays colorful text to the console, the color changes every <delay> milliseconds{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}rgbtxt <speed> <band size> <text> {BLUE.decode()}: {CYAN.decode()}Displays text with a rainbow gradient to the console, the rainbow speed and width are configurable{RESET.decode()}") 
                print(f"{RED.decode()}- {CYAN.decode()}figlet <font> <text> {BLUE.decode()}: {CYAN.decode()}Displays the text as ascii art to the console, you can change the style using the font{RESET.decode()}")
                print(f"{RED.decode()}- {CYAN.decode()}cfiglet <font> <color> <text> {BLUE.decode()}: {CYAN.decode()}Displays the colored text as ascii art to the console, you can change the style using the font{RESET.decode()}") 
                print(f"{RED.decode()}- {CYAN.decode()}rgbfiglet <font> <speed> <band size> <text> {BLUE.decode()}: {CYAN.decode()}Displays big text with a rainbow gradient to the console, the rainbow speed and width are configurable{RESET.decode()}") 
                print(f"{RED.decode()}- {CYAN.decode()}link <url> <text> {BLUE.decode()}: {CYAN.decode()}Displays a hyperlink with the specified text{RESET.decode()}") 

            elif command == "exit":
                print("Shutting down...")
                running = False
                run_thread.join()
            
            elif command == "reset":
                current_payload = payload.Reset()
            
            elif command.startswith("wipe"):
                if command == "wipe":
                    permanent = False
                elif command == "wipe permanent":
                    permanent = True
                else:
                    print("Usage: wipe [permanent]")
                    continue
                current_payload = payload.Wipe(permanent)
            
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
                current_payload = payload.Bell(delay)

            elif command.startswith("txt "):
                text = command.removeprefix("txt ")
                current_payload = payload.PrintText(text.encode())

            elif command.startswith("ctxt "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: ctxt <color> <text>")
                    continue
                color = payload.parse_color(split[1])
                text = " ".join(split[2:])
                current_payload = payload.PrintColoredText(text.encode(), color)

            elif command.startswith("fulltxt "):
                text = command.removeprefix("fulltxt ")
                current_payload = payload.PrintFullscreenText(text.encode())
            
            elif command.startswith("cfulltxt "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: cfulltxt <color> <text>")
                    continue
                color = payload.parse_color(split[1])
                text = " ".join(split[2:])
                current_payload = payload.PrintFullscreenText(text.encode(), color)
            
            elif command.startswith("rgb "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: rgb <millis> <text>")
                    continue

                try:
                    speed = int(split[1])
                except:
                    print("Please provide the speed as an integer")
                    return
                
                text = " ".join(split[2:])
                current_payload = payload.PrintRainbowText(text.encode(), speed)
            
            elif command.startswith("rgbtxt "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: rgbtxt <speed> <band size> <text>")
                    continue

                try:
                    speed = int(split[1])
                except:
                    print("Please provide the speed as an integer")
                    continue
                
                try:
                    band_size = int(split[2])
                except:
                    print("Please provide the band size as an integer")
                    continue
                
                text = " ".join(split[3:])
                current_payload = payload.PrintRGBText([text.encode()], speed, band_size)

            elif command.startswith("figlet "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: figlet <font> <text>")
                    continue
                figlet = pyfiglet.Figlet(font=split[1])
                text = " ".join(split[2:])
                figlet_text = figlet.renderText(text)
                current_payload = payload.PrintFullscreenText(figlet_text.encode())
            
            elif command.startswith("cfiglet "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: cfiglet <font> <color> <text>")
                    continue
                figlet = pyfiglet.Figlet(font=split[1])
                color = payload.parse_color(split[2])
                text = " ".join(split[3:])
                figlet_text = figlet.renderText(text)
                current_payload = payload.PrintFullscreenText(figlet_text.encode(), color)
            
            elif command.startswith("rgbfiglet "):
                split = command.split(" ")
                if len(split) <= 2:
                    print("Usage: rgbfiglet <font> <speed> <band size> <text>")
                    continue
                figlet = pyfiglet.Figlet(font=split[1])

                try:
                    speed = int(split[2])
                except:
                    print("Please provide the speed as an integer")
                    continue
                
                try:
                    band_size = int(split[3])
                except:
                    print("Please provide the band size as an integer")
                    continue
                
                text = " ".join(split[4:])
                figlet_text = figlet.renderText(text)
                current_payload = payload.PrintRGBText(figlet_text.encode().split(b"\n"), speed, band_size)

            elif command.startswith("link "):
                split = command.split(" ")
                if len(split) >= 4 and split[1] == "post":
                    url = split[2]
                    text = " ".join(split[3:])
                    encoded = payload.format_link(url.encode(), text.encode())
                    current_payload = payload.PrintText(encoded)
                elif len(split) == 3 and split[1] == "start":
                    # start a new link
                    url = split[2]
                    current_payload = payload.PrintText(ANSI_OSC + b"8;;" + url.encode() + ANSI_ST)
                elif len(split) == 2 and split[1] == "stop":
                    current_payload = payload.PrintText(OSC8_LINK_END)
                else:
                    print("You fucked up")

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