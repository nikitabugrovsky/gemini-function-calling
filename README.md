# Gemini Function Calling Weather Chatbot

This project demonstrates the function-calling feature of Google's Gemini large language models. The Python script creates a simple chatbot that can retrieve the current temperature for a given location by using a custom function.

## How it Works

This project is using **Strategy design pattern** to handle different methods of communicating with the Gemini API. This approach decouples the main application logic from the specific API client implementations, making the system cleaner and more extensible.

**Date:** July 17, 2025

The core logic is organized as follows:

1.  **`gemini-chatbot.py`:** This is the single entry point for the application. It accepts a command-line argument to select which API client "strategy" to use (`genai` or `openai`). It contains the main chat loop, which is now agnostic to the underlying API library.

2.  **`clients/` directory:** This module contains the different strategies for communicating with the LLM.
    *   **`api_client.py`:** An abstract base class that defines a common interface (`generate_content`, `get_function_call`, etc.) that all concrete clients must implement.
    *   **`genai_client.py`:** A concrete strategy that implements the `ApiClient` interface using the `google-genai` library.
    *   **`openai_client.py`:** A concrete strategy that implements the `ApiClient` interface using the `openai` library with Gemini's compatible endpoint.

3.  **`tools/` directory:**
    *   **`weather_tool.py`:** This module encapsulates the logic for the `get_current_temperature` function, including its communication with external geocoding and weather APIs.

When the chatbot runs, it uses the selected client to send the user's prompt to the Gemini model. The model can then issue a function call, which the main script executes via the `weather_tool` module.

## Dependencies

This project uses `uv` to manage dependencies. The required Python libraries for the application are:

*   `google-genai`: The official Python library for the Google AI SDK.
*   `openai`: The library for the OpenAI API, used to connect to Gemini's OpenAI-compatible endpoint.
*   `requests`: A simple, yet elegant, HTTP library for the weather tool.

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

You can run the chatbot using the main `gemini-chatbot.py` script. Use the `--client` flag to specify which API library to use.

To run the `google-genai` client implementation:
```bash
make gemini-genai
```

To run the `openai` library client implementation:
```bash
make gemini-openai
```
If you do not provide a `--client` flag, it will default to using `genai`.

## Gemini Function Calling

The core of this project is the function-calling feature of the Gemini model. This is implemented through the following components:

*   **`tools/weather_tool.py`:** This module contains the *implementation* of the `get_current_temperature` function and the detailed `WEATHER_TOOL_INSTRUCTIONS`.

*   **`clients/genai_client.py`, `clients/genai_client.py` & `clients/openai_client.py`:** Each client module contains its own library-specific `WEATHER_TOOL` dictionary. This dictionary *defines* the function for the model in the format required by its respective library (`google-genai` or `openai`).

This separation ensures that the tool's implementation is centralized, while the API-specific definitions live alongside the client logic.
