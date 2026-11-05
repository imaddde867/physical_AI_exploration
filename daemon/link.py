"""Line transport over any binary stream (e.g. serial.Serial); see protocol.py."""
from daemon import protocol


class Link:
    def __init__(self, stream):
        self.stream = stream

    def send(self, msg):
        self.stream.write(protocol.encode(msg))

    def recv(self):
        """Next valid message, or None on EOF/timeout. Invalid lines raise ValueError."""
        line = self.stream.readline(protocol.MAX_LINE + 1)
        return protocol.decode(line) if line else None
