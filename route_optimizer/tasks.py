from celery import shared_task
import requests
from geopy.distance import geodesic
import polyline
from scipy.spatial import KDTree
from .models import FuelStation
import logging
import folium
from folium.plugins import MarkerCluster
import uuid
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@shared_task  # This can remain as a shared task, not bound to a specific queue  
def fetch_route_and_fuel_stops(start_coords, finish_coords):  

    """Background task to fetch route and fuel stops."""  
    # Step 2: Call the OpenStreetMap routing API to get the route  
    route_result = get_route.delay(start_coords, finish_coords)  
    route_data = route_result.get(timeout=10)  

    # Step 3: Find optimal fuel stops along the route  
    optimal_stops, total_cost = find_fuel_stops.delay(route_data).get(timeout=20)  

    # Store the map in the maps directory  
    route_map_id = str(uuid.uuid4())  
    BASE_DIR = Path(__file__).resolve().parent.parent

    map_file_path = f"{os.path.join(BASE_DIR, 'maps', f'route_map_{route_map_id}.html')}"  # Save in maps directory  

    generate_route_map.delay(route_data, optimal_stops, map_file_path)  

    map_url = f"http://ap-dev-vm-atr:8000/static/route_map_{route_map_id}.html"  # Update the URL to access maps  

    logger.info("Map generation triggered, URL: %s", map_url)  

    return {"map_url": map_url, "total_cost": total_cost}   


@shared_task(queue='get_route_task')  # Assign to 'get_route_task' queue
def get_route(start_coords, finish_coords):
    """Call OpenStreetMap routing API to get the route between two coordinates."""
    url = f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{start_coords[1]},{start_coords[0]};{finish_coords[1]},{finish_coords[0]}?overview=false&geometries=polyline&steps=true"
    logger.info(url)
    headers = {
        "User-Agent": "FuelRouteOptimizer/1.0 (your_email@example.com)"  # Replace with your app's name and contact info
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Parse JSON response
    else:
        logger.error(f"Failed to fetch route: {response.status_code}, {response.text}")
        return None

@shared_task(queue='find_fuel_stops_task')  # Assign to 'find_fuel_stops_task' queue
def find_fuel_stops(route_data):
    """Optimized function to find fuel stops along the route."""
    total_cost = 0
    optimal_stops = []
    vehicle_range = 500  # miles
    fuel_efficiency = 10  # miles per gallon

    # Decode the entire route polyline once
    all_route_coords = decode_entire_route(route_data)

    # Define a bounding box to filter fuel stations
    min_lat, min_lon, max_lat, max_lon = get_bounding_box(all_route_coords)

    # Fetch only relevant fuel stations from the database
    fuel_stations = FuelStation.objects.filter(
        lat__gte=min_lat, lat__lte=max_lat,
        lon__gte=min_lon, lon__lte=max_lon
    ).values('name', 'lat', 'lon', 'retail_price')

    logger.info(f"Filtered {len(fuel_stations)} stations within route bounds.")

    # Build a k-d tree for fuel stations
    station_coords = [(float(station['lat']), float(station['lon'])) for station in fuel_stations]
    station_tree = KDTree(station_coords)
    
    station_data = {
        (float(station['lat']), float(station['lon'])): {
            "name": station['name'],
            "price_per_gallon": station['retail_price']
        }
        for station in fuel_stations
    }
    sample_rate = 100
    all_route_coords = all_route_coords[::sample_rate]

    # Query the k-d tree for nearby stations
    for coord in all_route_coords:
        lat, lon = coord
        nearby_indices = station_tree.query_ball_point([lat, lon], vehicle_range / 69)  # Convert miles to degrees
        for index in nearby_indices:
            station_lat, station_lon = station_coords[index]
            station_info = station_data[(station_lat, station_lon)]

            # Calculate precise geodesic distance
            distance_to_station = geodesic((lat, lon), (station_lat, station_lon)).miles

            if distance_to_station <= vehicle_range:
                fuel_needed = distance_to_station / fuel_efficiency
                total_cost += station_info['price_per_gallon'] * fuel_needed
                optimal_stops.append({
                    'station_name': station_info['name'],
                    'price_per_gallon': station_info['price_per_gallon'],
                    'location': (station_lat, station_lon),
                    'distance_to_station': distance_to_station
                })

    return optimal_stops, total_cost

def decode_entire_route(route_data):
    """Decode all route polylines and return a list of coordinates."""
    legs = route_data['routes'][0].get('legs', [])
    all_coords = []
    for leg in legs:
        for step in leg.get('steps', []):
            all_coords.extend(polyline.decode(step['geometry']))
    return all_coords

def get_bounding_box(coords):
    """Calculate a bounding box around the route coordinates with minimal buffer."""
    if not coords:
        raise ValueError("Coordinates list cannot be empty.")

    latitudes = [coord[0] for coord in coords]
    longitudes = [coord[1] for coord in coords]

    # Calculate the spread of the coordinates
    lat_range = max(latitudes) - min(latitudes)
    lon_range = max(longitudes) - min(longitudes)

    # Define a buffer as a small percentage of the range
    buffer = max(lat_range, lon_range) * 0.02  # 5% of the larger range

    # Ensure the buffer has a minimum value to avoid a zero-sized bounding box
    min_buffer = 0.01  # Adjust as needed
    buffer = max(buffer, min_buffer)

    return (
        min(latitudes) - buffer, min(longitudes) - buffer,
        max(latitudes) + buffer, max(longitudes) + buffer
    )

@shared_task(queue='generate_route_map_task')
def generate_route_map(route_data, fuel_stops, map_file_path):  
    """Generate or update a Folium map with the route and fuel stops."""  

    # Initialize map centered around the starting point  
    first_step = route_data['routes'][0]['legs'][0]['steps'][0]  
    start_lat, start_lon = first_step['maneuver']['location']  
    route_map = folium.Map(location=[start_lat, start_lon], zoom_start=10)  

    # Plot the route  
    all_coords = decode_entire_route(route_data)  
    folium.PolyLine(all_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)  

    # Plot fuel stops  
    marker_cluster = MarkerCluster().add_to(route_map)  
    for stop in fuel_stops:  
        folium.Marker(  
            location=stop['location'],  
            popup=f"{stop['station_name']} - ${stop['price_per_gallon']} per gallon",  
            icon=folium.Icon(color="green")  
        ).add_to(marker_cluster)  

    # Render the map to an HTML string  
    map_html = route_map._repr_html_()  

    # Save the HTML file to the specified file path  
    with open(map_file_path, 'w') as f:  
        f.write(map_html)  

    logger.info("Map saved to: %s", map_file_path) 