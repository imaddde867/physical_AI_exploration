"""The real USB serial port as a stream for daemon.link.Link; stdlib only."""
import glob
import os
import select
import termios


def open_raw(path):
    """The port, with echo and line translation off so JSON arrives unmodified."""
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY)
    saved = termios.tcgetattr(fd)
    raw = saved[:]
    raw[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP
                | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)
    raw[1] &= ~termios.OPOST
    raw[2] = (raw[2] & ~(termios.CSIZE | termios.PARENB)) | termios.CS8
    raw[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, raw)
    return fd, saved


def find_port(argv=()):
    if len(argv) > 1:
        return argv[1]
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    return ports[0] if ports else None


class Port:
    """readline/write over a raw fd. readline returns b"" after `timeout` s with no full line."""

    def __init__(self, path, timeout=0.1):
        self.fd, self.saved = open_raw(path)
        self.timeout, self.buf = timeout, b""

    def write(self, data):
        os.write(self.fd, data)

    def readline(self, limit):
        if b"\n" not in self.buf[:limit] and len(self.buf) < limit:
            if select.select([self.fd], [], [], self.timeout)[0]:
                chunk = os.read(self.fd, 512)
                if not chunk:
                    raise OSError("port closed")  # unplugged: the fd stays readable at EOF
                self.buf += chunk
        i = self.buf.find(b"\n", 0, limit) + 1
        if not i and len(self.buf) >= limit:
            i = limit  # overlong: hand it over so Link can reject it
        if not i:
            return b""  # partial line, kept for the next call
        line, self.buf = self.buf[:i], self.buf[i:]
        return line

    def close(self):
        try:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)
        except termios.error:
            pass  # the device is already gone
        os.close(self.fd)
