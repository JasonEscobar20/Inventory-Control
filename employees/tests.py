from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from employees.models import Employee


class EmployeesExportTests(TestCase):
	def setUp(self):
		# Create user and login
		self.user = get_user_model().objects.create_user(
			username='tester', email='tester@example.com', password='pass12345'
		)
		self.client.force_login(self.user)

		# Seed some employees
		Employee.objects.create(code='E001', first_name='Ana', last_name='Zamora')
		Employee.objects.create(code='E002', first_name='Luis', last_name='Alvarez')

	def test_download_csv(self):
		url = reverse('employees:employees_download') + '?format=csv'
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertIn('text/csv', resp['Content-Type'])
		self.assertIn('attachment; filename=', resp['Content-Disposition'])
		content = resp.content.decode('utf-8')
		self.assertIn('Código', content)
		self.assertIn('E001', content)

	def test_download_xlsx_default(self):
		url = reverse('employees:employees_download')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resp['Content-Type'])
		self.assertIn('.xlsx', resp['Content-Disposition'])
