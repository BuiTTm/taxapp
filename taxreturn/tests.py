from django.test import TestCase, Client
from .models import TaxReturn
from django.contrib.auth.models import User

class TaxReturnTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                    username='foo', email='foo@bar', 
                    password='bar')
        self.logged_in = self.client.login(
            username='foo',
            password='pass'
        )
        TaxReturn.objects.create(title="TestUnit", sin="123456789", user=self.user)


    def test_TaxReturn_sin_numeric(self):
        tax_r1 = TaxReturn.objects.get(title="TestUnit")
        self.assertEqual(tax_r1.sin, "123456789")


    def test_TaxReturn_check_user(self):
        tax_r1 = TaxReturn.objects.get(title="TestUnit")
        self.assertEqual(tax_r1.user, self.user)