from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse

from products.models import Product, Brand
from geo.models import Country, UserProfile


class ProductBulkUploadTests(TestCase):
	def setUp(self):
		# Countries
		self.country_gt = Country.objects.create(name='Guatemala', code='GT')
		self.country_sv = Country.objects.create(name='El Salvador', code='SV')

		# User with profile country GT
		self.user = get_user_model().objects.create_user('tester', 'tester@example.com', 'pass12345')
		profile = self.user.profile
		profile.country = self.country_gt
		profile.save()
		self.client.force_login(self.user)

		# Existing brand
		self.brand = Brand.objects.create(name='ACME', country=self.country_gt)
		Product.objects.create(sku='SKU1', description='Old Desc', brand=self.brand, country=self.country_gt)

	def test_bulk_upload_create_and_update(self):
		# CSV content: update SKU1, create SKU2 (same country), error on foreign country SV
		csv_content = (
			'sku,description,brand,country\n'
			'SKU1,New Desc,ACME,GT\n'
			'SKU2,Second Prod,ACME,GT\n'
			'SKU3,Third Prod,BETA,SV\n'
		)
		upload = SimpleUploadedFile('products.csv', csv_content.encode('utf-8'), content_type='text/csv')
		url = reverse('products:product_bulk_upload')
		resp = self.client.post(url, {'file': upload, 'create_brands': 'on'})
		self.assertEqual(resp.status_code, 200)
		# Verify counts in context
		self.assertContains(resp, 'Creados: 1')  # Only SKU2 created for GT
		self.assertContains(resp, 'Actualizados: 1')  # SKU1 updated
		# SKU3 should error due to country mismatch
		self.assertIn('País del registro (SV) no coincide', resp.content.decode())
		self.assertTrue(Product.objects.filter(sku='SKU2', country=self.country_gt).exists())
		self.assertEqual(Product.objects.get(sku='SKU1').description, 'New Desc')

	def test_bulk_upload_missing_columns(self):
		csv_content = 'sku,description\nSKU10,Desc Only\n'
		upload = SimpleUploadedFile('bad.csv', csv_content.encode('utf-8'), content_type='text/csv')
		url = reverse('products:product_bulk_upload')
		resp = self.client.post(url, {'file': upload})
		self.assertEqual(resp.status_code, 200)
		self.assertIn('Faltan columnas requeridas', resp.content.decode())
