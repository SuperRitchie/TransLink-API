import os
import requests
from google.transit import gtfs_realtime_pb2
from gmplot import gmplot

# APIkey = config('KEY')
# mapAPI = config('gmapKEY')

# Fetch API keys from environment variables
API_KEY = os.getenv('TRANSLINK_API')
GMAP_API_KEY = os.getenv('GMAP_API')

url = f'https://gtfsapi.translink.ca/v3/gtfsposition?apikey={API_KEY}'

# Fetch GTFS data
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get(url)
feed.ParseFromString(response.content)

# Initialize lists to store latitudes, longitudes, info for markers, and icon URLs
lats = []
lons = []
infos = []
icons = []

# URLs to SVG icons
left_green_arrow_url = 'https://upload.wikimedia.org/wikipedia/commons/e/ed/Green_Arrow_Left.svg'
right_green_arrow_url = 'https://upload.wikimedia.org/wikipedia/commons/a/a0/Green_Arrow_Right.svg'
left_red_arrow_url = 'https://upload.wikimedia.org/wikipedia/commons/0/0d/Red_Arrow_Left.svg'
right_red_arrow_url = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Red_Arrow_Right.svg'

# Process feed data to extract coordinates and other information
for entity in feed.entity:
    if entity.HasField('vehicle'):
        vehicle = entity.vehicle
        route_number = vehicle.trip.route_id if vehicle.trip.route_id else "N/A"
        
        # Only process if the route is "37807"
        if route_number == "37807":
            position = vehicle.position
            vehicle_number = int(vehicle.vehicle.id) if vehicle.vehicle.id else 0
            direction_id = vehicle.trip.direction_id if vehicle.trip.HasField('direction_id') else -1
            direction = "Outbound" if direction_id == 0 else "Inbound" if direction_id == 1 else "Unknown"
            
            # Determine which SVG icon to use based on direction and vehicle number
            if direction == "Inbound":
                if vehicle_number >= 18000:
                    icon_url = left_green_arrow_url
                else:
                    icon_url = left_red_arrow_url
            elif direction == "Outbound":
                if vehicle_number >= 18000:
                    icon_url = right_green_arrow_url
                else:
                    icon_url = right_red_arrow_url
            else:
                continue  # Skip if direction is unknown
            
            # Create a marker info string with direction information
            info = f'Vehicle: {vehicle_number}, Route: {route_number}, Direction: {direction}'
            
            # Append data to lists
            lats.append(position.latitude)
            lons.append(position.longitude)
            infos.append(info)
            icons.append(icon_url)

# Check if we have any plotted points and calculate the map center based on their average location
if lats and lons:
    map_center_lat = sum(lats) / len(lats)
    map_center_lon = sum(lons) / len(lons)
else:
    # Default location if no points were plotted
    map_center_lat = 49.2827  # Vancouver
    map_center_lon = -123.1207  # Vancouver

# Create a GoogleMapPlotter object centered at the average plotted points
gmap = gmplot.GoogleMapPlotter(map_center_lat, map_center_lon, 12, apikey=GMAP_API_KEY)

# Plot the bus locations with custom markers
for lat, lon, info, icon in zip(lats, lons, infos, icons):
    gmap.marker(lat, lon, title=info, icon=icon)

# Save the map to an HTML file
gmap.draw('index.html')
