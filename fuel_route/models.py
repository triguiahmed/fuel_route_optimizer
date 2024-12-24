from django.db import models

class FuelStation(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    latitude = models.FloatField()
    longitude = models.FloatField()
    retail_price = models.FloatField()

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state} (${self.retail_price})"
