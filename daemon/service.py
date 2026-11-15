"""Run the Buddy OS host on the real port: keepalive, hello resync, module supervision, reconnect.

Usage: python3 -m daemon [/dev/cu.usbmodemXXXX]   (Ctrl-C to stop)
"""
import asyncio
import sys

from daemon.host import Ctx, Host, supervise
from daemon.link import Link
from daemon.port import Port, find_port

STEP_S = 0.5  # reconcile cadence; the reconciler pings every 1.5 s when nothing changed
RETRY_S = 1.0


async def pump(link, host):
    """Feed device messages to the host; a bad line (REPL banner, noise) is skipped."""
    while True:
        try:
            msg = await asyncio.to_thread(link.recv)
        except ValueError:
            continue
        if msg:
            host.on_message(msg)


async def session(host, modules, log=print, step_s=STEP_S, until=None):
    """Drive one host until its port errors (OSError) or `until()` is true."""
    tasks = [asyncio.create_task(supervise(n, run, Ctx(host, n), log)) for n, run in modules.items()]
    reader = asyncio.create_task(pump(host.link, host))
    try:
        while not (until and until()):
            host.step()
            if reader.done():
                reader.result()  # re-raises the OSError that ended the read
            await asyncio.sleep(step_s)
    finally:
        for t in (*tasks, reader):
            t.cancel()


async def run(argv, modules=None, log=print):
    while True:
        path = find_port(argv)
        try:
            if path is None:
                raise OSError("no /dev/cu.usbmodem* port")
            port = Port(path)
            log(f"connected {path}")
            try:
                await session(Host(Link(port)), modules or {}, log)
            finally:
                port.close()
        except OSError as e:
            log(f"waiting for device: {e}")
            await asyncio.sleep(RETRY_S)


def main(argv):
    try:
        asyncio.run(run(argv))
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
