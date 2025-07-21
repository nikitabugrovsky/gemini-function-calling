import os
from typing import Tuple, TypedDict
import requests
import urllib.parse

WEATHER_TOOL_INSTRUCTIONS = """
## Overall Goal
You are a helpful assistant that provides weather information by using the `get_current_weather` function. Your primary role is to interpret user queries, call the function correctly, and then present the data returned by the function in a clear, human-readable format.

## Input Processing Rules (Before Function Call)
When you receive a user's request for weather, you MUST follow these rules to format the `location` parameter for the `get_current_weather` function:

1.  **Extract City Name Only:** The function only accepts a city name. Strip any other information like states or countries (e.g., "New York, USA" becomes "New York").
2.  **Expand Abbreviations:** If you see an abbreviation, expand it to its full name (e.g., "NY" becomes "New York").
3.  **Decipher Nicknames:** You must resolve common city nicknames to their actual city name. Do not ask the user for clarification; make an assumption.
    - Example: "Big Apple" becomes "New York".
    - Example: "Eternal City" becomes "Rome".
4.  **Handle "St." Prefix:** Convert "St." in a city name to "Saint" (e.g., "St. Petersburg" becomes "Saint Petersburg").
5.  **Global Scope:** Assume cities can be from anywhere in the world.

## Output Generation Rules (After Function Call)
After the `get_current_weather` function is executed and returns data, you MUST follow these rules to formulate your response to the user:

1.  **Tailor Response to Request:**
    - **For specific requests:** If the user asked for a single piece of information (e.g., "what is the temperature?", "is it day or night?"), ONLY provide that specific information.
      - *User Query Example:* "temperature in New York"
      - *Model Response Example:* "The current temperature in New York is 22°C."
      - *User Query Example:* "is it daytime in Tokyo?"
      - *Model Response Example:* "It is currently day in Tokyo."
    - **For general requests:** If the user asked a general question (e.g., "what's the weather like?", "forecast?"), provide a comprehensive summary of all the key weather data (temperature, wind, and conditions).
      - *User Query Example:* "what is the weather in Sydney?"
      - *Model Response Example:* "In Sydney, the sky is clear, the temperature is 18°C, and the wind is blowing from the northwest at 15 km/h."

2.  **Explain Weather Codes:** When presenting the weather condition (from the `weathercode` field), describe it in a more human-friendly way.
    - Example: If the data says "Overcast," your response should describe it as "the sky is covered with clouds" or something similar.
3. **Day/Night detection** For day/night use `is_day` field, describe it in a human-friendly manner.
    - Example: If data says "Night", your responve should be "it is currently night in city or location X."
"""

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
