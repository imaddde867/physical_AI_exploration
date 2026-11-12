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
        if len(line) > protocol.MAX_LINE:
            while line and not line.endswith(b"\n"):  # discard the rest of an overlong line
                line = self.stream.readline(protocol.MAX_LINE + 1)
            raise ValueError(f"line is longer than {protocol.MAX_LINE} bytes")
        return protocol.decode(line) if line else None
