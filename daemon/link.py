"""Line transport over any binary stream (e.g. serial.Serial); see protocol.py."""
from daemon import protocol

DISCARD_READS = 4  # bounded recovery: never wait for a newline that may never arrive


class Link:
    def __init__(self, stream):
        self.stream = stream

    def send(self, msg):
        self.stream.write(protocol.encode(msg))

    def recv(self):
        """Next valid message, or None on EOF/timeout. Invalid lines raise ValueError.

        An overlong line is discarded for at most DISCARD_READS reads, so the wait is
        bounded by the stream's own timeout instead of an unbounded newline hunt.
        """
        line = self.stream.readline(protocol.MAX_LINE + 1)
        if len(line) > protocol.MAX_LINE:
            for _ in range(DISCARD_READS):
                if line.endswith(b"\n"):
                    break
                line = self.stream.readline(protocol.MAX_LINE + 1)
                if not line:
                    break
            raise ValueError(f"line is longer than {protocol.MAX_LINE} bytes")
        return protocol.decode(line) if line else None
