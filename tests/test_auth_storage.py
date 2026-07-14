import json
import os
import tempfile
import unittest

from app import app


class AuthStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.users_path = os.path.join(self.tmpdir.name, 'users.json')
        app.config.update(TESTING=True, USERS_FILE=self.users_path)
        with open(self.users_path, 'w', encoding='utf-8') as handle:
            json.dump([], handle)
        self.client = app.test_client()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_register_and_login_persist_to_json(self):
        register_response = self.client.post('/api/register', json={
            'name': 'Ada Lovelace',
            'email': 'ada@example.com',
            'password': 'secret123'
        })
        self.assertEqual(register_response.status_code, 200)
        self.assertEqual(register_response.get_json()['user']['email'], 'ada@example.com')

        with open(self.users_path, 'r', encoding='utf-8') as handle:
            stored_users = json.load(handle)
        self.assertEqual(len(stored_users), 1)
        self.assertEqual(stored_users[0]['email'], 'ada@example.com')

        login_response = self.client.post('/api/login', json={
            'email': 'ada@example.com',
            'password': 'secret123'
        })
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.get_json()['user']['name'], 'Ada Lovelace')


if __name__ == '__main__':
    unittest.main()
