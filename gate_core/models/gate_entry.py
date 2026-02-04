# gate_core/models/gate_entry.py

from django.db import models
from gate_core.enums import GateEntryStatus
from .base import BaseModel

class GateEntryBase(BaseModel):
    entry_no = models.CharField(max_length=30, unique=True)

    status = models.CharField(
        max_length=30,
        choices=GateEntryStatus.choices,
        default=GateEntryStatus.DRAFT
    )

    is_locked = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.pk:
            old = self.__class__.objects.get(pk=self.pk)
            if old.is_locked:
                raise ValueError("Gate entry is locked and cannot be modified")
        super().save(*args, **kwargs)


    class Meta:
        abstract = True
