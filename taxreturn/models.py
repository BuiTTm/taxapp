from django.db import models
from django.contrib.auth.models import User

tax_year_choices = (
    ('2021', '2021'),
    ('2020', '2020'),
    ('2019', '2019'),
    )

class TaxReturn(models.Model):
    title = models.CharField(max_length=100)
    year = models.CharField(max_length=4)
    full_name = models.CharField(blank=True, max_length=100)
    sin = models.CharField(blank=True, max_length=9)
    memo = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paymentcompleted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
