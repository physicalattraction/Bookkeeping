from django.db import models

from common.behaviors import Equalable, Timestampable, UUIDable


class Contact(UUIDable, Timestampable, Equalable, models.Model):
    name = models.CharField(max_length=64)
    account = models.CharField(max_length=64, help_text='Bank account of the contact')
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
