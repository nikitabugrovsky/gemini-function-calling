import os
import requests
import urllib.parse

WEATHER_TOOL_INSTRUCTIONS ="\
    Here are the instructions that should be followed when get_current_temperature is invoked: \
    1. Only city name should be taken as a parameter for function invocation.\
    For e.g. New York, USA should become New York\
    2. Abbreviations should be expanded. For e.g. NY should become New York.\
    3. City nicknames should be desyphered into real names. Do not request to clarify, assume instead.\
    For e.g. Big Apple should become New York.\
    4. Cities are not limited to a particular country but rather to the whole world.\
    For e.g. Eternal City should become Rome.\
    5. Cities that have St. in their name should translate to Saint.\
    For e.g. St. Petersburg should become Saint Petersburg.\
    6. When asked about weather assume that you've been asked about temperature.\
    For e.g. What's the weather in Karachi? really means: What's the temperature in Karachi.\
    "

def _get_location_coordinates(location):
    """Gets the coordinates for a given location."""
    url = "https://geocode.maps.co/search?"
    params = {"city": location}
    api_key = os.environ.get("GEOCODE_API_KEY")
    if api_key:
            params["api_key"] = api_key
    geocode_url = url + urllib.parse.urlencode(params)
    geocode_response = requests.get(geocode_url)
    geocode_response.raise_for_status()
    geocode_data = geocode_response.json()
    if not geocode_data:
        return {"error": "Could not find location: no geocode_data"}

    latitude = geocode_data[0]["lat"]
    longitude = geocode_data[0]["lon"]

    return latitude, longitude

def _get_location_temperature(latitude, longitude):
    """Gets the current temperature for a given latitude & longtitude."""
    url = "https://api.open-meteo.com/v1/forecast?"
    params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    open_meteo_url = url + urllib.parse.urlencode(params)
    response = requests.get(open_meteo_url)
    response.raise_for_status()
    data = response.json()

    if "current_weather" in data:
        return {"temperature": data["current_weather"]["temperature"]}
    else:
        return {"error": "Could not get weather data"}

def get_current_temperature(location):
    """Gets the current temperature for a given location."""
    if not location:
        return {"error": "Could not find location: model did not provide location"}
    latitude, longitude = _get_location_coordinates(location)
    temperature = _get_location_temperature(latitude, longitude)

    return temperature
