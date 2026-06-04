import os
import json
import requests
from google.transit import gtfs_realtime_pb2

API_KEY = os.getenv("TRANSLINK_API")
GMAP_API_KEY = os.getenv("GMAP_API")

if not API_KEY:
    raise ValueError("missing TRANSLINK_API")

if not GMAP_API_KEY:
    raise ValueError("missing GMAP_API")

url = f"https://gtfsapi.translink.ca/v3/gtfsposition?apikey={API_KEY}"

response = requests.get(url, timeout=15)
response.raise_for_status()

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

buses = []

for entity in feed.entity:
    if not entity.HasField("vehicle"):
        continue

    vehicle = entity.vehicle
    route_number = vehicle.trip.route_id if vehicle.trip.route_id else "N/A"

    if route_number != "37807":
        continue

    if not vehicle.HasField("position"):
        continue

    position = vehicle.position

    if position.latitude == 0 and position.longitude == 0:
        continue

    if not (-90 <= position.latitude <= 90 and -180 <= position.longitude <= 180):
        continue

    vehicle_number = int(vehicle.vehicle.id) if vehicle.vehicle.id else 0
    direction_id = vehicle.trip.direction_id if vehicle.trip.HasField("direction_id") else -1
    direction = "Outbound" if direction_id == 0 else "Inbound" if direction_id == 1 else "Unknown"
    marker_color = "green" if vehicle_number >= 18000 else "red"

    buses.append({
        "lat": position.latitude,
        "lng": position.longitude,
        "route": route_number,
        "vehicle": vehicle_number,
        "direction": direction,
        "color": marker_color,
        "info": f"Vehicle: {vehicle_number}, Route: {route_number}, Direction: {direction}"
    })

if buses:
    map_center_lat = sum(bus["lat"] for bus in buses) / len(buses)
    map_center_lng = sum(bus["lng"] for bus in buses) / len(buses)
else:
    map_center_lat = 49.2827
    map_center_lng = -123.1207

html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TransLink bus map</title>

  <style>
    html, body {{
      height: 100%;
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
    }}

    #map {{
      width: 100vw;
      height: 100dvh;
    }}

    .bus-label {{
      background: rgba(255, 255, 255, 0.94);
      border: 2px solid #333;
      border-radius: 999px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
      padding: 5px 8px;
      font-size: 12px;
      line-height: 1.1;
      white-space: nowrap;
      transform: translateY(-6px);
      user-select: none;
    }}

    .bus-label.green {{
      border-color: #188038;
    }}

    .bus-label.red {{
      border-color: #d93025;
    }}

    .bus-route {{
      font-weight: 700;
    }}

    .bus-details {{
      font-size: 10px;
      opacity: 0.85;
    }}

    @media (max-width: 600px) {{
      .bus-label {{
        font-size: 11px;
        padding: 4px 6px;
      }}

      .bus-details {{
        display: none;
      }}
    }}
  </style>
</head>

<body>
  <div id="map"></div>

  <script>
    const buses = {json.dumps(buses)};

    async function initMap() {{
      const {{ AdvancedMarkerElement }} = await google.maps.importLibrary("marker");

      const map = new google.maps.Map(document.getElementById("map"), {{
        center: {{ lat: {map_center_lat}, lng: {map_center_lng} }},
        zoom: 12,
        mapId: "DEMO_MAP_ID",
        gestureHandling: "cooperative",
        minZoom: 10,
        maxZoom: 17,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
        clickableIcons: false,
        restriction: {{
          latLngBounds: {{
            north: 49.55,
            south: 48.95,
            west: -123.35,
            east: -122.40
          }},
          strictBounds: false
        }}
      }});

      const bounds = new google.maps.LatLngBounds();

      buses.forEach((bus) => {{
        const label = document.createElement("div");
        label.className = `bus-label ${{bus.color}}`;

        const route = document.createElement("div");
        route.className = "bus-route";
        route.textContent = `Route ${{bus.route}}`;

        const details = document.createElement("div");
        details.className = "bus-details";
        details.textContent = `#${{bus.vehicle}} ${{bus.direction}}`;

        label.append(route, details);

        const position = {{ lat: bus.lat, lng: bus.lng }};
        bounds.extend(position);

        new AdvancedMarkerElement({{
          map,
          position,
          title: bus.info,
          content: label,
          collisionBehavior: google.maps.CollisionBehavior.OPTIONAL_AND_HIDES_LOWER_PRIORITY
        }});
      }});

      if (buses.length > 0) {{
        map.fitBounds(bounds, 60);
      }}
    }}

    window.initMap = initMap;
  </script>

  <script
    src="https://maps.googleapis.com/maps/api/js?key={GMAP_API_KEY}&callback=initMap&v=weekly"
    defer>
  </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html)