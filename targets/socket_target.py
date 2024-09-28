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
            while True:
                data = conn.recv(1024)
                if data == None or len(data) == 0: break
                print(data.decode())
        except KeyboardInterrupt: break # this will only trigger once it receives any data, i don't knwo how to fix it right now
        except:
            print("Client disconnected!")