import unittest
from app import app

class BasicFlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_endpoint(self):
        """Test home route loads successfully with HTML content."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cloud & DevOps Lab Application', response.data)
        self.assertIn(b'Serving Pod / Host', response.data)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('pod_name', data)

    def test_info_endpoint(self):
        """Test info endpoint."""
        response = self.app.get('/info')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['version'], '1.0.0')
        self.assertIn('hostname', data)

    def test_greet_endpoint(self):
        """Test greet endpoint with query parameter."""
        response = self.app.get('/api/greet?name=Tester')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Hello, Tester!')
        self.assertIn('served_by_pod', data)

if __name__ == '__main__':
    unittest.main()
