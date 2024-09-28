import socket

class Printer:
    # print the bytes to the target's console
    def print(self, bytes):
        pass

    # ran when the program exits, so you can clean up
    def close(self): pass

class SocketPrinter(Printer):
    def __init__(self, addr) -> None:
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)
    
    def print(self, bytes):
        self.socket.sendall(bytes)

    def close(self):
        self.socket.close()