import unittest
from websocket_service import WebSocketService

class TestWebSocketService(unittest.TestCase):
    def setUp(self):
        self.websocket = WebSocketService()

    def test_connect(self):
        result = self.websocket.connect('ws://example.com')
        self.assertTrue(result)

    def test_disconnect(self):
        self.websocket.connect('ws://example.com')
        result = self.websocket.disconnect()
        self.assertTrue(result)

    def test_send_message(self):
        self.websocket.connect('ws://example.com')
        result = self.websocket.send_message('Hello, World!')
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
