import socket

class Printer:
    # print the bytes to the target's console
    def print(self, bytes: bytes):
        pass

    # ran when the program exits, so you can clean up
    def close(self): pass

# prints it to our own console, so you don't have to spin up another service when testing
class SelfPrinter(Printer):
    def print(self, bytes: bytes):
        print(bytes.decode())

# printer for `targets/socket_target.py`. only sends the bytes to the other side via a TCP socket
class SocketPrinter(Printer):
    def __init__(self, addr) -> None:
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)
    
    def print(self, bytes: bytes):
        self.socket.sendall(bytes)

    def close(self):
        self.socket.close()