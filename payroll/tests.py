from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from .models import Employee, TimeOffBalance, LeaveRequest

class PayrollTests(TestCase):
    def setUp(self):
        # Create a test employee user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.employee = Employee.objects.create(name='testuser', email='test@example.com')

        # Create a test manager user
        self.manager = User.objects.create_user(username='manageruser', password='managerpass')
        managers_group = Group.objects.create(name='Managers')
        self.manager.groups.add(managers_group)

        self.client = Client()

    def test_login(self):
        # Test employee login
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # Redirect to home

    def test_pay_history_view(self):
        # Employee views pay history
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/pay_history/')
        self.assertEqual(response.status_code, 200)

    def test_time_off_balance_view(self):
        # Employee views time off balance
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/time_off_balance/')
        self.assertEqual(response.status_code, 200)

    def test_leave_request_submission(self):
        # Employee submits a leave request
        self.client.login(username='testuser', password='testpass')
        response = self.client.post('/request_leave/', {
            'start_date': '2025-05-01',
            'end_date': '2025-05-05',
            'leave_type': 'Holiday',
            'reason': 'Vacation'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(LeaveRequest.objects.filter(employee=self.employee).exists())

    def test_manager_can_view_users(self):
        # Manager views user list
        self.client.login(username='manageruser', password='managerpass')
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_manager_can_view_employees(self):
        # Manager views employee list
        self.client.login(username='manageruser', password='managerpass')
        response = self.client.get('/employees/')
        self.assertEqual(response.status_code, 200)

    def test_manager_can_log_pay(self):
        # Manager opens log pay page
        self.client.login(username='manageruser', password='managerpass')
        response = self.client.get('/log_pay/')
        self.assertEqual(response.status_code, 200)

    def test_manager_can_manage_time_off(self):
        # Manager opens time off management page
        self.client.login(username='manageruser', password='managerpass')
        response = self.client.get('/manage_time_off/')
        self.assertEqual(response.status_code, 200)

    def test_manager_can_manage_leave_requests(self):
        # Manager opens leave request management page
        self.client.login(username='manageruser', password='managerpass')
        response = self.client.get('/manage_leave_requests/')
        self.assertEqual(response.status_code, 200)



        
