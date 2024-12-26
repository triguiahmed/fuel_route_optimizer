import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FuelStation
import logging
import json
from geopy.distance import geodesic
import polyline
from scipy.spatial import KDTree
from rest_framework.permissions import AllowAny
import folium
from folium.plugins import MarkerCluster
from .tasks import fetch_route_and_fuel_stops  # Import the Celery task
import functools

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  
)
logger = logging.getLogger(__name__)

class FuelStopAPI(APIView):
    permission_classes = [AllowAny]  

    def get(self, request, *args, **kwargs):
        start_location = request.query_params.get('start')
        finish_location = request.query_params.get('finish')

        if not start_location or not finish_location:
            return Response({"error": "Both start and finish locations are required"}, status=400)

        # Step 1: Get coordinates for start and finish locations using Nominatim API
        start_coords, finish_coords = self.get_location_coords(start_location), self.get_location_coords(finish_location)
        
        if not start_coords or not finish_coords:
            return Response({"error": "Could not resolve one of the locations"}, status=400)

        # Call Celery task to handle route and fuel stop processing and wait for the result  
        result = fetch_route_and_fuel_stops.apply(args=[start_coords, finish_coords])  
        
        # You can return the result of the task in the response  
        return JsonResponse({  
            "message": "Route processing completed",  
            "result": result.get()  # This will block until the task is done and return the result  
        })  

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
                logger.info(f"Latitude: {lat}, Longitude: {lon}")
                return lat, lon
        return None, None
