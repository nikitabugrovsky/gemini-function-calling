import os
from typing import Tuple, TypedDict
import requests
import urllib.parse

WEATHER_TOOL_INSTRUCTIONS = "\
    Here are the instructions that should be followed when get_current_weather is invoked:\
    1. Only city name should be taken as a parameter for function invocation.\
    For e.g. New York, USA should become New York\
    2. Abbreviations should be expanded. For e.g. NY should become New York.\
    3. City nicknames should be desyphered into real names. Do not request to clarify, assume instead.\
    For e.g. Big Apple should become New York.\
    4. Cities are not limited to a particular country but rather to the whole world.\
    For e.g. Eternal City should become Rome.\
    5. Cities that have St. in their name should translate to Saint.\
    For e.g. St. Petersburg should become Saint Petersburg.\
    6. When asked about weather and returning value for wethercode specifically \
    try to explain it in a more human friendly way. For e.g. Overcast should be transformed into clouds covering a large part of the sky.\
"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light intensity",
    53: "Drizzle: Moderate intensity",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light intensity",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight intensity",
    63: "Rain: Moderate intensity",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light intensity",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight intensity",
    73: "Snow fall: Moderate intensity",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight intensity",
    81: "Rain showers: Moderate intensity",
    82: "Rain showers: Violent intensity",
    85: "Snow showers: Slight intensity",
    86: "Snow showers: Heavy intensity",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

class InitWeatherData(TypedDict):
    time: str
    interval: int
    temperature: float
    windspeed: float
    winddirection: float
    is_day: int
    weathercode: int

class FinalWeatherData(TypedDict):
    temperature: float
    windspeed: float
    winddirection: str
    is_day: str
    weathercode: str

def _get_wind_direction(degrees: float) -> str:
    match degrees:
        case x if 348.75 <= x <= 360 or 0 <= x < 11.25:
            return "N"
        case x if 11.25 <= x < 33.75:
            return "NNE"
        case x if 33.75 <= x < 56.25:
            return "NE"
        case x if 56.25 <= x < 78.75:
            return "ENE"
        case x if 78.75 <= x < 101.25:
            return "E"
        case x if 101.25 <= x < 123.75:
            return "ESE"
        case x if 123.75 <= x < 146.25:
            return "SE"
        case x if 146.25 <= x < 168.75:
            return "SSE"
        case x if 168.75 <= x < 191.25:
            return "S"
        case x if 191.25 <= x < 213.75:
            return "SSW"
        case x if 213.75 <= x < 236.25:
            return "SW"
        case x if 236.25 <= x < 258.75:
            return "WSW"
        case x if 258.75 <= x < 281.25:
            return "W"
        case x if 281.25 <= x < 303.75:
            return "WNW"
        case x if 303.75 <= x < 326.25:
            return "NW"
        case x if 326.25 <= x < 348.75:
            return "NNW"
        case _:
            return "Unknown"

def _map_weather_data(init_weather_data: InitWeatherData) -> FinalWeatherData:
    final_weather_data: FinalWeatherData = {
        "temperature": init_weather_data["temperature"],
        "windspeed": init_weather_data["windspeed"],
        "winddirection": _get_wind_direction(init_weather_data["winddirection"]),
        "is_day": "Day" if init_weather_data["is_day"] == 1 else "Night",
        "weathercode": WEATHER_CODES.get(init_weather_data["weathercode"], "Unknown"),
    }

    return final_weather_data

def _get_location_coordinates(location: str) -> Tuple[float, float]:
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

    latitude = geocode_data[0]["lat"]
    longitude = geocode_data[0]["lon"]

    return latitude, longitude

def _get_location_weather(latitude: float, longitude: float) -> InitWeatherData:
    """Gets the current weather for a given latitude & longtitude."""
    url = "https://api.open-meteo.com/v1/forecast?"
    params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    open_meteo_url = url + urllib.parse.urlencode(params)
    response = requests.get(open_meteo_url)
    response.raise_for_status()
    data = response.json()

    init_weather_data: InitWeatherData = data["current_weather"]
    return init_weather_data

def get_current_weather(location: str) -> FinalWeatherData:
    """Gets the current weather for a given location."""
    latitude, longitude = _get_location_coordinates(location)
    weather = _get_location_weather(latitude, longitude)
    weather = _map_weather_data(weather)
    return weather
