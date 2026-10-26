"""A small, auditable newline-delimited JSON protocol."""
import json

FACES = frozenset({"neutral", "happy", "sad", "sleepy", "surprised", "thinking"})

def face_command(face: str) -> bytes:
    if face not in FACES:
        raise ValueError(f"unsupported face: {face}")
    return (json.dumps({"cmd": "face", "value": face}, separators=(",", ":")) + "\n").encode("utf-8")

def parse_response(line: bytes) -> dict:
    data = json.loads(line.decode("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("type"), str):
        raise ValueError("response must be an object containing a string 'type'")
    return data
