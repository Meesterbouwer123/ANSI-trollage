# Sample application vulnerable to ANSI injection.
# used to test this tool, don't deploy it in the real world (it's useless anyways)

# start a server on port 9999 and print every line that gets sent to the console
import socket

with socket.socket() as s:
    s.bind(("localhost", 9999))
    s.listen()
    print ("Listening on port 9999")
    
    while True:
        conn, addr = s.accept()
        try:
            old = b""
            while True:
                data = conn.recv(1024) # read blocks of 1024 bytes
                if data == None or len(data) == 0: break
                try:
                    print((old + data).decode(), end='', flush=True) # print the raw bytes to the screen
                    old = b""
                except:
                    old += data
        except KeyboardInterrupt: break # this will only trigger once it receives any data, i don't knwo how to fix it right now
        except Exception as e:
            print("Client disconnected! (%s)" % str(e))