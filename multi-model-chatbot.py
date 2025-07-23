# gemini-chatbot.py
import argparse
import json
from clients.api_client import ApiClient
from tools.weather_tool import get_current_weather

class Color:
    """Return Colorized Output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

def get_api_client(client_type: str, model_type: str) -> ApiClient:
    """Factory function to get the appropriate API client."""
    if client_type == "gemini-genai":
        from clients.genai_client import GenAIClient
        return GenAIClient(model=model_type)
    elif client_type == "gemini-openai":
        from clients.openai_client import OpenAIClient
        return OpenAIClient(model=model_type)
    elif client_type == "gemma-openai":
        from clients.ollama_client import OllamaClient
        return OllamaClient(model=model_type)
    else:
        raise ValueError(f"Unknown client type: {client_type}")

def main(client_type: str, model_type: str):
    """Executes the chatbot flow using the selected API client."""
    client = get_api_client(client_type, model_type)

    print(f"{Color.BOLD}Multi-model Chatbot {Color.GREEN}d[o_0]b{Color.END} (Client: {client_type}, model: {model_type}, type {Color.RED}'exit'{Color.END} to {Color.BOLD}quit{Color.END})")
    print(f"{Color.BOLD}={Color.END}" * 40)

    while True:
        user_input = input(f"{Color.YELLOW}{Color.BOLD}You:{Color.END} ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        client.generate_content(user_input, function_execution_result=None)

        function_call = client.get_function_call()
        if function_call:
            print(f"{Color.GREEN}{Color.BOLD}d[o_0]b{Color.BLUE}[Tool: None]:{Color.END} I am gonna call {function_call['name']} tool with arguments: {json.dumps(function_call['arguments'])}")
            result = get_current_weather(**function_call["arguments"])
            client.generate_content(user_input=None, function_execution_result=result)
            chatbot_message = client.get_text_response()
            print(f"{Color.GREEN}{Color.BOLD}d[o_0]b{Color.BLUE}[Tool: {function_call["name"]}]:{Color.END} {chatbot_message}".strip())
        else:
            text_response = client.get_text_response()
            chatbot_message = f"{text_response}".strip()
            print(f"{Color.GREEN}{Color.BOLD}d[o_0]b{Color.BLUE}[Tool: None]:{Color.END} {chatbot_message}".strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-model Chatbot with Function Calling")
    parser.add_argument(
        "--client",
        type=str,
        choices=["gemini-genai", "gemini-openai", "gemma-openai"],
        default="gemini-genai",
        help="The API client library to use."
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["gemini-2.5-flash-lite-preview-06-17", "gemini-2.5-flash", "gemini-2.5-pro", "gemma3:1b"],
        default="gemini-2.5-flash-lite-preview-06-17",
        help="LLM model to use."
    )
    args = parser.parse_args()
    main(args.client, args.model)
