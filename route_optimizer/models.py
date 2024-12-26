from django.db import models

class FuelStation(models.Model):
    opis_truckstop_id = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    rack_id = models.IntegerField(default=0) 
    retail_price = models.FloatField()
    lat = models.FloatField()
    lon = models.FloatField()
    class Meta:
        indexes = [
            models.Index(fields=['lat', 'lon']),  # Index for lat/lon
            models.Index(fields=['city']),  # Index for city if needed
        ]
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state} (${self.retail_price})"
