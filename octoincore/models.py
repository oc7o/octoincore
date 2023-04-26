import uuid

from django.db import models


class OctoModel(models.Model):
    """Base model for all models in OctoInCore."""

    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the string representation of the model."""
        return self.name
