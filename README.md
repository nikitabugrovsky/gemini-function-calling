# Multimodel Function Calling Chatbot

This project demonstrates function calling with large language models, supporting both Google's Gemini API and local models via Ollama. The Python script creates a simple chatbot that can retrieve the current weather for a given location by using a custom function, showcasing the flexibility of a strategy-based design.

## How it Works

This project is using **Strategy design pattern** to handle different methods of communicating with the Gemini API. This approach decouples the main application logic from the specific API client implementations, making the system cleaner and more extensible.

**Date:** July 21, 2025

The core logic is organized as follows:

1.  **`multi-model-chatbot.py`:** This is the single entry point for the application. It accepts a command-line argument to select which API client "strategy" to use (`genai` or `openai`). It contains the main chat loop, which is now agnostic to the underlying API library.

2.  **`clients/` directory:** This module contains the different strategies for communicating with the LLM.
    *   **`api_client.py`:** An abstract base class that defines a common interface (`generate_content`, `get_function_call`, etc.) that all concrete clients must implement.
    *   **`genai_client.py`:** A concrete strategy that implements the `ApiClient` interface using the `google-genai` library.
    *   **`openai_client.py`:** A concrete strategy that implements the `ApiClient` interface using the `openai` library with Gemini's compatible endpoint.
    *   **`ollama_client.py`:** A concrete strategy for running models locally using **[Ollama](https://ollama.com/)**. It uses the `openai` library to connect to Ollama's OpenAI-compatible API endpoint, allowing for local, offline-capable chatbot functionality without relying on cloud-based APIs.

3.  **`tools/` directory:**

    *   **`weather_tool.py`:** This module encapsulates the logic for the `get_current_weather` function. It now uses the [Open-Meteo API](https://open-meteo.com/) for both geocoding (to get coordinates for a location) and for retrieving weather data. The function now returns a more detailed weather forecast, including temperature, wind speed, wind direction, and whether it is day or night. The `weathercode` is also translated into a human-readable description.

When the chatbot runs, it uses the selected client to send the user's prompt to the Gemini model. The model can then issue a function call, which the main script executes via the `weather_tool` module.

## Enhanced Chatbot Flow: Two-Step Function Calls

A significant enhancement to this project is the implementation of a two-step process for function calls. This ensures that the chatbot not only executes the requested function but also provides a more natural and human-readable response based on the function's output.

Here’s how it works:

1.  **Initial API Call:** The user's input is sent to the Gemini model. The model determines if a function call is needed to fulfill the request.

2.  **Function Execution:** If the model decides to call a function (e.g., `get_current_weather`), the chatbot executes the function with the provided arguments and captures the result.

3.  **Second API Call:** The result of the function call is then sent back to the Gemini model in a second API call.

4.  **Human-Readable Output:** The model processes the function's result and generates a final, user-friendly response. For example, instead of just printing the raw weather data, the chatbot will now say something like, "The current temperature in New York is 25°C."

This two-step process creates a more interactive and intuitive user experience. This workflow is a practical example of a pattern known as **Retrieval Augmented Generation (RAG)**. While RAG is often associated with retrieving data from static documents, our implementation uses a live API call for retrieval. In this context, **Function Calling is the mechanism that enables this specific, real-time implementation of the RAG pattern.**

## Dependencies

- This project uses `uv` to manage dependencies.
- `ollama` is required to run `ollama_client.py` implementation.

The required Python libraries for the application are:

*   `google-genai`: The official Python library for the Google AI SDK.
*   `openai`: The library for the OpenAI API, used to connect to Gemini's OpenAI-compatible endpoint.
*   `requests`: A simple, yet elegant, HTTP library for the weather tool.

## Local Model Setup with Ollama

A key feature of this project is the ability to run the chatbot against a model deployed locally on your machine.

1.  **Install Ollama:** First, you need to install Ollama. You can find the download instructions on their official website:
    *   <https://ollama.com/download>

2.  **Pull the Model:** Once Ollama is running, you must pull the model used by our client. We are using the slim, open `gemma3:1b` model. Open your terminal and run:
    ```bash
    ollama run gemma3:1b
    ```
    You can find more information about the model here: <https://ollama.com/library/gemma3>

## API Keys

To run this script, you will need to set up your Gemini API key as an environment variable.

First, for the Gemini API, you'll need to set the `GEMINI_API_KEY`:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
Note: The Ollama client does not require any API keys, as it runs entirely on your local machine.

```

The Open-Meteo API, which is used for geocoding and weather data, is free to use without an API key. However, for higher usage, you can optionally add an `OPENMETEO_API_KEY`:

```bash
export OPENMETEO_API_KEY="YOUR_OPENMETEO_API_KEY"
```

## How to Run

You can run the chatbot using the main `gemini-chatbot.py` script. Use the `--client` flag to specify which API library to use.

To run the `google-genai` client implementation:
To run the `ollama` client implementation against your local model:
```bash
make gemma-openai
```

```bash
make gemini-genai
```

To run the `openai` library client implementation:
```bash
make gemini-openai
```
If you do not provide a `--client` flag, it will default to using `genai`.

## Function Calling Implementation

The core of this project is the function-calling feature of the Gemini model. This is implemented through the following components:

*   **`tools/weather_tool.py`:** This module contains the *implementation* of the `get_current_weather` function and the detailed `WEATHER_TOOL_INSTRUCTIONS`.

*   **`clients/ollama_client.py`, `clients/genai_client.py` & `clients/openai_client.py`:** Each client module contains its own library-specific `WEATHER_TOOL` dictionary. This dictionary *defines* the function for the model in the format required by its respective library (`google-genai` or `openai`).

This separation ensures that the tool's implementation is centralized, while the API-specific definitions live alongside the client logic.
