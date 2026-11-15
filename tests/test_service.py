import asyncio
import os
import select
import threading
import unittest

from daemon import protocol
from daemon.host import Host
from daemon.link import Link
from daemon.port import Port
from daemon.service import session
from firmware.rp2040.main import OVERFLOW, LineReader, handle, make_hello


class FakeDevice(threading.Thread):
    """The firmware's own LineReader and handle() behind a pty, as the board would answer."""

    def __init__(self, master):
        super().__init__(daemon=True)
        self.master, self.heard, self.stop = master, [], False

    def run(self):
        reader, hello, gaze = LineReader(), [make_hello()], [0.0, 0.0]
        try:
            while not self.stop:
                if not select.select([self.master], [], [], 0.02)[0]:
                    continue
                data = os.read(self.master, 256)
                if not data:
                    return
                for ch in data.decode():
                    line = reader.feed(ch)
                    if line is None or line is OVERFLOW:
                        continue
                    self.heard.append(line)
                    os.write(self.master, handle(line, gaze, hello)[0].encode())
        except OSError:
            return  # test closed the pty


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.master, slave = os.openpty()
        self.port = Port(os.ttyname(slave), timeout=0.02)
        self.device = FakeDevice(self.master)
        self.device.start()
        self.host = Host(Link(self.port))

    def unplug(self):
        self.device.stop = True
        self.device.join()
        os.close(self.master)  # the pty hangs up, as a pulled cable does
        self.master = None

    def tearDown(self):
        if self.master is not None:
            self.unplug()
        self.port.close()

    def test_first_ping_gets_a_hello_and_the_host_resyncs(self):
        asyncio.run(asyncio.wait_for(
            session(self.host, {}, step_s=0.02, until=lambda: self.host.boot_id), 5))
        self.assertEqual(self.host.boot_id and len(self.host.boot_id), 8)
        self.assertEqual(protocol.decode(self.device.heard[0]), {"v": 1, "t": "ping"})

    def test_module_state_reaches_the_device(self):
        async def look(ctx):
            ctx.show("ambient", {"face": {"v": 1, "t": "face", "x": 0.5}}, ttl=60)
            await asyncio.sleep(60)

        asyncio.run(asyncio.wait_for(
            session(self.host, {"look": look}, step_s=0.02,
                    until=lambda: any('"x":0.5' in h for h in self.device.heard)), 5))

    def test_unplugging_ends_the_session_with_oserror(self):
        self.unplug()
        with self.assertRaises(OSError):
            asyncio.run(asyncio.wait_for(session(self.host, {}, step_s=0.02), 5))


if __name__ == "__main__":
    unittest.main()
