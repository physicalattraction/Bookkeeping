import uuid

from django.db import models
from django.utils import timezone


class Equalable(models.Model):
    class Meta:
        abstract = True

    def __eq__(self, other) -> bool:
        """
        Return whether self is considered the same object as other

        This method is used in validation before saving objects to the database.
        This means that some of the fields can be absent.
        """

        for field in self._meta.fields:
            if hasattr(self, field.name) and not hasattr(other, field.name):
                return False
            if not hasattr(self, field.name) and hasattr(other, field.name):
                return False
            if hasattr(self, field.name) and hasattr(other, field.name) and \
                    getattr(self, field.name) != getattr(other, field.name):
                return False
        return True


class Timestampable(models.Model):
    """
    With this behavior mixed in, an object gets two fields that are filled automatically on
    creation or update of the object.

    This class inherits from models.Model, since it adds fields to the Django model. Otherwise,
    these Django does not recognize these fields, e.g. if you want to use them for sorting.
    """

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now = timezone.now()

        if not self.created_at:
            self.created_at = now
        self.updated_at = now

        super().save(*args, **kwargs)


class UUIDable(models.Model):
    """
    With this behavior mixed in, an object gets a field that is automatically filled with a UUID string when an object
    is created

    This class inherits from models.Model, since it adds fields to the Django model. Otherwise,
    these Django does not recognize these fields, e.g. if you want to use them for sorting.
    """

    uuid = models.CharField(max_length=64, editable=False, primary_key=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.uuid)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = self.generate_uuid()
        super().save(*args, **kwargs)

    def generate_uuid(self) -> str:
        return str(uuid.uuid4()).upper()
