import unittest
from app import app

class CloudOpsPulseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_dashboard_route(self):
        """Test home route loads successfully with HTML content."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CloudOps Pulse', response.data)
        self.assertIn(b'Active Pod Identifier', response.data)

    def test_health_endpoint(self):
        """Test Kubernetes liveness probe endpoint."""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'healthy')
        self.assertIn('pod_name', json_data)

    def test_info_endpoint(self):
        """Test system telemetry JSON endpoint."""
        response = self.app.get('/api/info')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('hostname', json_data)
        self.assertIn('python_version', json_data)

    def test_task_operations(self):
        """Test adding and toggling tasks."""
        # Add task
        response = self.app.post('/api/tasks', json={"title": "Automated Unit Test Task"})
        self.assertEqual(response.status_code, 201)
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        task_id = json_data['task']['id']

        # Toggle task
        response_toggle = self.app.post(f'/api/tasks/{task_id}/toggle')
        self.assertEqual(response_toggle.status_code, 200)

if __name__ == '__main__':
    unittest.main()
