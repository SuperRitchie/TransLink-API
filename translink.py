from urllib import response
import requests
import json
from decouple import config
import gmplot

APIkey = config('KEY')
url = "https://api.translink.ca/rttiapi/v1/buses?apikey=" + APIkey # + "&stopNo=53987"
header = {'content-type': 'application/json', 'accept': 'text/plain'}
r = requests.get(url, headers=header)
data = r.json()
#print(data)
#print all of the routes in the data of the API
#print routes in the data variable

#generate a random number between 1 and 20
#print the route number of the random number

#generate a random number between 1 and 20
#print the stop number of the random number

def printStop(data):
    latitudes = []
    longitudes = []
    #store all of the longitudes in the longitudes list
    count = 0
    for bus in data:
        latitudes.append(float(bus['Latitude']))
        longitudes.append(float(bus['Longitude']))
        count += 1
        #print(bus)
        #convert latitudes to float and store in latitudes
        #print bus latitude
        #print(bus['Latitude'])
        
            
        #print(bus)
        #print("Bus " + bus['RouteNo'])
    #print(count)
    return latitudes, longitudes
#printStop(data)
latitudes, longitudes = printStop(data)
print(latitudes)
print(longitudes)
gmap3 = gmplot.GoogleMapPlotter(49, -123, 13)
gmap3.scatter(latitudes, longitudes, '#FF0000', size = 40, marker = False)

gmap3.draw("C:\\Users\\Ritchie\\TransLink-API\\map.html")

#print(r.headers['content-type'])