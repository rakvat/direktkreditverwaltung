import datetime

from django.test import TestCase
from .models import Contact


class ContactModelTests(TestCase):

    def test_dummy(self):
        assert 2+2==4

    def test_create_contact(self):
        contact = Contact(first_name="Emma", last_name="Goldman")
        assert contact is not None
