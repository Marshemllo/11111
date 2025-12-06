import unittest
from app import app, socketio

class TestChatApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.socketio_client = socketio.test_client(app)

    def test_login_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'OODaiP Login', response.data)

    def test_login_success(self):
        response = self.app.post('/', data={
            'nickname': 'TestUser',
            'password': '123456',
            'server_url': 'http://localhost:5000'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TestUser', response.data)

    def test_login_failure(self):
        response = self.app.post('/', data={
            'nickname': 'TestUser',
            'password': 'wrongpassword',
            'server_url': 'http://localhost:5000'
        })
        self.assertIn(b'Invalid Password', response.data)

    def test_socket_connection(self):
        self.assertTrue(self.socketio_client.is_connected())
        
    def test_socket_join(self):
        self.socketio_client.emit('join', {'username': 'TestUser'})
        received = self.socketio_client.get_received()
        found = False
        for msg in received:
            if msg['name'] == 'status':
                args = msg.get('args')
                data = args if isinstance(args, dict) else (args[0] if isinstance(args, list) else {})
                if 'TestUser has entered the room' in data.get('msg', ''):
                    found = True
        self.assertTrue(found)

    def test_socket_message(self):
        self.socketio_client.emit('join', {'username': 'TestUser'})
        self.socketio_client.get_received()
        
        self.socketio_client.emit('message', {'username': 'TestUser', 'msg': 'Hello World'})
        received = self.socketio_client.get_received()
        
        found = False
        for msg in received:
            if msg['name'] == 'message':
                args = msg.get('args')
                # Handle dict vs list discrepancy in test client
                data = args if isinstance(args, dict) else (args[0] if isinstance(args, list) else {})
                
                if data.get('username') == 'TestUser' and data.get('msg') == 'Hello World':
                    found = True
        
        self.assertTrue(found, f"Message not found. Received: {received}")

if __name__ == '__main__':
    unittest.main()
