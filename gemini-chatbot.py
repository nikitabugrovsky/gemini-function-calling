# gemini-chatbot.py
import argparse
import json
from clients.api_client import ApiClient
from tools.weather_tool import get_current_weather

MODEL = "gemini-2.0-flash-lite"

class Color:
    """Return Colorized Output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

def get_api_client(client_type: str) -> ApiClient:
    """Factory function to get the appropriate API client."""
    if client_type == "genai":
        from clients.genai_client import GenAIClient
        return GenAIClient(model=MODEL)
    elif client_type == "openai":
        from clients.openai_client import OpenAIClient
        return OpenAIClient(model=MODEL)
    else:
        raise ValueError(f"Unknown client type: {client_type}")

def main(client_type: str):
    """Executes the chatbot flow using the selected API client."""
    client = get_api_client(client_type)

    print(f"{Color.BOLD}Gemini Chatbot {Color.GREEN}d[o_0]b{Color.END} (Client: {client_type}, type {Color.RED}'exit'{Color.END} to {Color.BOLD}quit{Color.END})")
    print(f"{Color.BOLD}={Color.END}" * 40)

    while True:
        user_input = input(f"{Color.YELLOW}{Color.BOLD}You:{Color.END} ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        client.generate_content(user_input, function_execution_result=None)

        function_call = client.get_function_call()
        if function_call:
            print(f"{Color.GREEN}{Color.BOLD}d[o_0]b:{Color.END} I am gonna call {function_call['name']} tool with arguments: {json.dumps(function_call['arguments'])}")
            result = get_current_weather(**function_call["arguments"])
            client.generate_content(user_input=None, function_execution_result=result)
            chatbot_message = client.get_text_response()
        else:
            text_response = client.get_text_response()
            chatbot_message = f"""I am not calling any tools at the moment. My response is: {text_response}""".strip()

        print(f"{Color.GREEN}{Color.BOLD}d[o_0]b:{Color.END} {chatbot_message}".strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini Chatbot with Function Calling")
    parser.add_argument(
        "--client",
        type=str,
        choices=["genai", "openai"],
        default="genai",
        help="The API client library to use."
    )
    args = parser.parse_args()
    main(args.client)
