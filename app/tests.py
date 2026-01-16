from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Employee

class EmployeeAPITestCase(TestCase):
    def setUp(self):
        """Set up test client and create test user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Authenticate
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_employee(self):
        """Test creating a new employee"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'department': 'Engineering',
            'role': 'Developer'
        }
        response = self.client.post('/api/employees/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().name, 'John Doe')

    def test_create_employee_duplicate_email(self):
        """Test creating employee with duplicate email returns 400"""
        Employee.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            department='HR',
            role='Manager'
        )
        data = {
            'name': 'John Doe',
            'email': 'jane@example.com',
            'department': 'Sales',
            'role': 'Analyst'
        }
        response = self.client.post('/api/employees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_empty_name(self):
        """Test creating employee with empty name returns 400"""
        data = {
            'name': '',
            'email': 'test@example.com',
        }
        response = self.client.post('/api/employees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_employees(self):
        """Test listing all employees"""
        Employee.objects.create(name='Alice', email='alice@example.com')
        Employee.objects.create(name='Bob', email='bob@example.com')
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_department(self):
        """Test filtering employees by department"""
        Employee.objects.create(
            name='Alice',
            email='alice@example.com',
            department='HR'
        )
        Employee.objects.create(
            name='Bob',
            email='bob@example.com',
            department='Engineering'
        )
        response = self.client.get('/api/employees/?department=HR')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['department'], 'HR')

    def test_retrieve_employee(self):
        """Test retrieving a single employee"""
        employee = Employee.objects.create(
            name='Charlie',
            email='charlie@example.com'
        )
        response = self.client.get(f'/api/employees/{employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Charlie')

    def test_retrieve_nonexistent_employee(self):
        """Test retrieving non-existent employee returns 404"""
        response = self.client.get('/api/employees/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_employee(self):
        """Test updating an employee"""
        employee = Employee.objects.create(
            name='David',
            email='david@example.com',
            role='Developer'
        )
        data = {'role': 'Senior Developer'}
        response = self.client.patch(f'/api/employees/{employee.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        employee.refresh_from_db()
        self.assertEqual(employee.role, 'Senior Developer')

    def test_delete_employee(self):
        """Test deleting an employee returns 204"""
        employee = Employee.objects.create(
            name='Eve',
            email='eve@example.com'
        )
        response = self.client.delete(f'/api/employees/{employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 0)

    def test_pagination(self):
        """Test pagination works correctly"""
        for i in range(15):
            Employee.objects.create(
                name=f'Employee {i}',
                email=f'emp{i}@example.com'
            )
        response = self.client.get('/api/employees/')
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])

    def test_unauthenticated_request(self):
        """Test that unauthenticated requests are rejected"""
        client = APIClient()  # New client without auth
        response = client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
