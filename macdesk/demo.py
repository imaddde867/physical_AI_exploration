"""Run: python3 -m macdesk.demo --simulate --face happy."""
import argparse
import json
import time
from macdesk.protocol import FACES, face_command, parse_response


def run_simulated(face: str, watch: bool = False) -> None:
    request = face_command(face)
    print("Mac -> ESP32:", request.decode().strip())
    print("ESP32 -> Mac:", json.dumps({"type": "ack", "face": face}))
    if watch:
        print("ESP32 -> Mac:", json.dumps({"type": "event", "name": "shake"}))
        print("Simulated event only; physical sensing is not exercised.")


def run_device(port: str, face: str, watch: bool = False, baudrate: int = 115200) -> None:
    try:
        import serial
    except ImportError as exc:
        raise SystemExit("Install dependency: python3 -m pip install -r requirements.txt") from exc
    with serial.Serial(port, baudrate=baudrate, timeout=2) as device:
        time.sleep(2)  # native CDC device may reset on connect
        device.reset_input_buffer()
        device.write(face_command(face))
        device.flush()
        for _ in range(8):
            data = device.readline()
            if not data:
                continue
            response = parse_response(data)
            print(response)
            if response["type"] == "ack" and response.get("face") == face:
                break
            if response["type"] == "error":
                raise RuntimeError(f"device error: {response}")
        else:
            raise TimeoutError("no matching acknowledgement; check USB port and firmware")
        if watch:
            print("Watching sensor events (Ctrl-C to stop) ...")
            try:
                while True:
                    data = device.readline()
                    if data:
                        print(parse_response(data))
            except KeyboardInterrupt:
                print("Stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="MacDesk Buddy USB face controller")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--simulate", action="store_true", help="no hardware required")
    choice.add_argument("--port", help="macOS serial port, e.g. /dev/cu.usbmodemXXXX")
    parser.add_argument("--face", choices=sorted(FACES), default="happy")
    parser.add_argument("--watch", action="store_true", help="show IMU motion events")
    args = parser.parse_args()
    if args.simulate:
        run_simulated(args.face, args.watch)
    else:
        run_device(args.port, args.face, args.watch)


if __name__ == "__main__":
    main()
