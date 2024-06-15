from django.db import models


class Claim(models.Model):
    insured = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)

    def __str__(self):
        return self.policy_number
