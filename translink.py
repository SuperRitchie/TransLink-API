import requests
from decouple import config
import gmplot
import time

APIkey = config('KEY')
mapAPI = config('gmapKEY')
url = "https://api.translink.ca/rttiapi/v1/buses?apikey=" + APIkey # + "&stopNo=53987"
header = {'content-type': 'application/json', 'accept': 'text/plain'}
r = requests.get(url, headers=header)
data = r.json()

def getLocation(data):
    latitudes = []
    longitudes = []
    destinations = []
    directions = []
    times = []
    routesNo = []
    
    for bus in data:
        latitudes.append(float(bus['Latitude']))
        longitudes.append(float(bus['Longitude']))
        destinations.append(bus['Destination'])
        directions.append(bus['Direction'])
        times.append(bus['RecordedTime'])
        routesNo.append(bus['RouteNo'])
        
        #only append for buses numbers between 7000 and 7999
        
        '''
        if(bus['VehicleNo'] >= '7000' and bus['VehicleNo'] <= '7999'):
            #print(bus)
            latitudes.append(float(bus['Latitude']))
            longitudes.append(float(bus['Longitude']))
            destinations.append(bus['Destination'])
            directions.append(bus['Direction'])
            times.append(bus['RecordedTime'])
            routesNo.append(bus['RouteNo'])
        '''
    return latitudes, longitudes, destinations, directions, times, len(latitudes), routesNo

latitudes, longitudes, destinations, directions, times, length, routesNo = getLocation(data)
averageLat = sum(latitudes)/len(latitudes)
averageLong = sum(longitudes)/len(longitudes)
print(averageLat), print(averageLong)

gmap3 = gmplot.GoogleMapPlotter(averageLat, averageLong, 13, apikey=mapAPI)
gmap3.scatter(latitudes, longitudes, '#ff0000')
for i in range(length):
    time.sleep(0.001)
    gmap3.marker(latitudes[i], longitudes[i], title = routesNo[i] + " " + destinations[i] + " " + directions[i] + " " + times[i])

time.sleep(5)
gmap3.draw("C:\\Users\\Ritchie\\TransLink-API\\map.html")

#print(r.headers['content-type'])