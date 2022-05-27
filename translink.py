from urllib import response
import requests
import json
from decouple import config

APIkey = config('KEY')
url = "https://api.translink.ca/rttiapi/v1/buses?apikey=" + APIkey + "&stopNo=53987"
header = {'content-type': 'application/json', 'accept': 'text/plain'}
r = requests.get(url, headers=header)
data = r.json()
print(data)
#print all of the routes in the data of the API
#print routes in the data variable

#generate a random number between 1 and 20
#print the route number of the random number

#generate a random number between 1 and 20
#print the stop number of the random number

def printStop(data):
    for bus in data:
        print(bus)
        print("Bus " + bus['RouteNo'])

printStop(data)
#print(r.headers['content-type'])