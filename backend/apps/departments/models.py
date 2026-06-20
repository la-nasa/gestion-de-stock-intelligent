from django.db import models
from core.models.base import BaseModel

class Department(BaseModel):
    class Type(models.TextChoices):
        ACADEMIC = "ACADEMIC", "Académique"
        ADMINISTRATIVE = "ADMINISTRATIVE", "Administratif"
        TECHNICAL = "TECHNICAL", "Technique"
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.ACADEMIC)
    campus = models.ForeignKey("campuses.Campus", on_delete=models.CASCADE, related_name="departments")
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["name"]
    def __str__(self): return f"{self.name}"