import csv
from django.core.management.base import BaseCommand
from route_optimizer.models import FuelStation

class Command(BaseCommand):
    help = "Load fuel station data from a CSV file."

    def handle(self, *args, **kwargs):
        file_path = '/app/route_optimizer/management/commands/fuel-prices-for-be-assessment.csv'
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                FuelStation.objects.create(
                    opis_truckstop_id=int(row["OPIS Truckstop ID"]), 
                    name=row["Truckstop Name"],
                    address=row["Address"],
                    city=row["City"],
                    state=row["State"],
                    latitude=float(row.get("Latitude", 0.0)),
                    longitude=float(row.get("Longitude", 0.0)),
                    rack_id=int(row["Rack ID"]), 
                    retail_price=float(row["Retail Price"]),
                )
        
        self.stdout.write(self.style.SUCCESS("Fuel data loaded successfully!"))
