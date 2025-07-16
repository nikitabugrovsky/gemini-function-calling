# Gemini Function Calling Weather Chatbot

This project demonstrates the function-calling feature of Google's Gemini large language models. The Python script creates a simple chatbot that can retrieve the current temperature for a given location by using a custom function.

## How it Works

The project now includes two separate implementations that demonstrate how to interact with the Gemini API using two different libraries: `google-genai` and `openai`.

In both implementations, the script interacts with the Gemini model and provides it with a tool definition for a function called `get_current_temperature`. When a user asks for the weather in a specific location, the model doesn't directly answer the question. Instead, it recognizes that it needs to use the provided tool and returns a "function call" to the script.

The script then executes the `get_current_temperature` function with the arguments provided by the model (the location). This process involves a few key APIs:

1.  **Gemini API:** The script communicates with the Gemini model using one of two libraries:
    *   **`google-genai`:** The official Python library for the Google AI SDK.
    *   **`openai`:** The popular library for the OpenAI API, which can be configured to work with Gemini's OpenAI-compatible endpoint.
2.  **Geocoding API (Optional):** To get the latitude and longitude of the given location. The API key for this service is optional, as it allows for unauthenticated requests. However, these are subject to severe throttling, and using an API key allows for a higher number of requests.
3.  **Open-Meteo API:** To get the current temperature for those coordinates.

Finally, the script prints the result of the function call, which includes the temperature.

## Dependencies

This project uses `uv` to manage dependencies and run the scripts. The required Python libraries are specified within each script.

### `gemini-genai.py`

*   `google-genai`: The official Python library for the Google AI SDK.
*   `requests`: A simple, yet elegant, HTTP library.

### `gemini-openai.py`

*   `openai`: The library for the OpenAI API.
*   `requests`: A simple, yet elegant, HTTP library.

## API Keys

To run this script, you will need to set up two API keys as environment variables.

First, for the Gemini API, you'll need to set the `GEMINI_API_KEY`:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Second optionally, you will need an API key from a geocoding service that is compatible with the [Geocode Earth](https://geocode.earth/) API. The script is configured to use the `https://geocode.maps.co/search` endpoint. Set it as an environment variable:

```bash
export GEOCODE_API_KEY="YOUR_GEOCODE_API_KEY"
```

## How to Run

You can run either of the two implementations using the following `make` commands:

To run the `google-genai` implementation:
```bash
make gemini-genai
```

To run the `openai` library implementation:
```bash
make gemini-openai
```

## Gemini Function Calling

The core of this project is the function-calling feature of the Gemini model. This is implemented through the following components in both scripts:

*   **`WEATHER_TOOL`:** This is a dictionary that defines the `get_current_temperature` function for the Gemini model. It includes the function's name, a description of what it does, and the parameters it expects (in this case, a `location`).

*   **`WEATHER_TOOL_INSTRUCTIONS`:** This is a set of instructions that guides the model on how to use the `get_current_temperature` function. It provides rules for handling different types of location inputs, such as expanding abbreviations, deciphering nicknames, and handling different phrasings of the weather question.

By providing the model with these tools and instructions, we enable it to go beyond simple text generation and interact with external systems to perform tasks.
