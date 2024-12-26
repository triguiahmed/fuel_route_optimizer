import csv
from django.core.management.base import BaseCommand
from route_optimizer.models import FuelStation
import requests

class Command(BaseCommand):
    help = "Load fuel station data from a CSV file."

    def handle(self, *args, **kwargs):
        file_path = '/app/route_optimizer/management/commands/fuel-prices-for-be-assessment.csv'
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            print("Loading fuel data...")
            for row in reader:
                corrdinates=self.get_location_coords(row["Truckstop Name"])
                FuelStation.objects.create(
                    opis_truckstop_id=int(row["OPIS Truckstop ID"]), 
                    name=row["Truckstop Name"],
                    address=row["Address"],
                    city=row["City"],
                    state=row["State"],
                    lat=corrdinates[0],
                    lon=corrdinates[1],
                    rack_id=int(row["Rack ID"]), 
                    retail_price=float(row["Retail Price"]),
                )
        
        self.stdout.write(self.style.SUCCESS("Fuel data loaded successfully!"))
    def get_location_coords(self, location):

        """Get coordinates for a location using Nominatim API."""
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json"
        }
        headers = {
            "User-Agent": "FuelRouteOptimizer/1.0 (your_email@example.com)"  # Replace with your app's name and contact info
        }
        response = requests.get(url, params=params, headers=headers)


        if response.status_code == 200:
                data = response.json()
                if data:  # Ensure data is not empty
                    lat, lon = data[0]['lat'], data[0]['lon']
                    return lat,lon
        return 0 , 0
