import unittest
from macdesk.protocol import FACES, face_command, parse_response

class ProtocolTests(unittest.TestCase):
    def test_supported_faces(self):
        for name in FACES:
            self.assertEqual(face_command(name).decode(), '{"cmd":"face","value":"%s"}\n' % name)

    def test_invalid_face_fails_closed(self):
        with self.assertRaises(ValueError):
            face_command("servo=180")

    def test_ack(self):
        self.assertEqual(parse_response(b'{"type":"ack","face":"happy"}\n')["face"], "happy")

    def test_missing_type(self):
        with self.assertRaises(ValueError):
            parse_response(b'{"foo":1}')

    def test_nonobject(self):
        with self.assertRaises(ValueError):
            parse_response(b'[]')

    def test_malformed_json(self):
        with self.assertRaises(ValueError):
            parse_response(b'bad')

if __name__ == "__main__":
    unittest.main()
