"""Write synthetic frames until 96 or ENOSPC. Do not construct the LCD framebuffer.

One bytearray(134400) is the only large allocation. write() and flush() are timed
separately; LittleFS may defer the erase to flush.
"""

FRAME = 134400
TARGET = 96
PATH = "bench-clip.bin"


def _fill(buf, index):
    block = bytearray(256)
    base = (index * 17) & 0xFF
    for i in range(256):
        block[i] = (i + base) & 0xFF
    view = memoryview(buf)
    offset = 0
    while offset < FRAME:
        view[offset:offset + 256] = block
        offset += 256


def _space():
    import os
    info = os.statvfs("/")
    return {"block": info[0], "total": info[2] * info[0], "free": info[3] * info[0]}


def _crc(buf):
    import binascii
    return binascii.crc32(memoryview(buf)) & 0xFFFFFFFF


def run():
    import gc
    import json
    import os
    import time

    gc.collect()
    print("HEAP_BEFORE", gc.mem_free())
    buf = bytearray(FRAME)
    gc.collect()
    print("HEAP_AFTER_BUF", gc.mem_free())
    try:
        os.remove(PATH)
    except OSError:
        pass
    print("STAT_BEFORE", json.dumps(_space()))
    stored = []
    written = 0
    write_us = []
    flush_us = []
    try:
        handle = open(PATH, "wb")
        try:
            for index in range(TARGET):
                _fill(buf, index)
                expect = _crc(buf)
                start = time.ticks_us()
                count = handle.write(buf)
                write_dt = time.ticks_diff(time.ticks_us(), start)
                if write_dt <= 0:
                    raise ValueError("clock did not advance")
                if count is not None and count != FRAME:
                    raise OSError("short write %s" % count)
                flush_start = time.ticks_us()
                handle.flush()
                flush_dt = time.ticks_diff(time.ticks_us(), flush_start)
                write_us.append(write_dt)
                flush_us.append(flush_dt)
                stored.append(expect)
                written = index + 1
                print("FRAME", index, write_dt, flush_dt)
        finally:
            handle.close()
    except OSError as exc:
        print("WRITE_FAIL", json.dumps({
            "error": repr(exc),
            "errno": getattr(exc, "errno", None),
            "frames_written": written,
            "free": _space()["free"],
        }))
    if write_us:
        total_us = 0
        flush_total = 0
        for sample in write_us:
            total_us += sample
        for sample in flush_us:
            flush_total += sample
        total_bytes = written * FRAME
        combined = total_us + flush_total
        print("WRITE_SUMMARY", json.dumps({
            "frames": written,
            "bytes": total_bytes,
            "write_mean_ms": (total_us / written) / 1000,
            "flush_mean_ms": (flush_total / written) / 1000,
            "write_mb_s": (total_bytes / total_us) if total_us else 0,
            "combined_mb_s": (total_bytes / combined) if combined else 0,
            "write_max_us": max(write_us),
            "flush_max_us": max(flush_us),
        }))
    print("STAT_AFTER", json.dumps(_space()))
    if written:
        checks = (0, written // 2, written - 1)
        handle = open(PATH, "rb")
        try:
            for index in checks:
                handle.seek(index * FRAME)
                count = handle.readinto(buf)
                file_crc = _crc(buf) if count == FRAME else None
                _fill(buf, index)
                regen = _crc(buf)
                print("READBACK", json.dumps({
                    "index": index,
                    "read": count,
                    "file_crc": file_crc,
                    "stored_crc": stored[index],
                    "regen_crc": regen,
                    "match": file_crc == stored[index] == regen,
                }))
        finally:
            handle.close()
    try:
        os.remove(PATH)
        print("REMOVED", PATH)
    except OSError as exc:
        print("REMOVE_FAIL", repr(exc))
    gc.collect()
    print("STAT_DELETED", json.dumps(_space()))
    print("FILES", sorted(os.listdir("/")))
    print("DONE")


if __name__ == "__main__":
    run()
