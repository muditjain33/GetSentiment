from django.db import models

# Create your models here.
class emailmodel(models.Model):
    objects = None
    id = models.AutoField(primary_key=True)
    email=models.EmailField()
    def __str__(self):
        return f"{self.email}"