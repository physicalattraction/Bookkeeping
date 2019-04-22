from django.db import IntegrityError
from django.test import TestCase

from contacts.models import Contact


class ContactTestCase(TestCase):
    def test_that_email_must_be_unique(self):
        Contact.objects.create(name='John Doe', email='johndoe@example.com')
        with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed: contacts_contact.email'):
            Contact.objects.create(name='John Doe', email='johndoe@example.com')

    def test_that_email_can_be_empty(self):
        Contact.objects.create(name='John Doe', email=None)
        Contact.objects.create(name='John Doe', email=None)
