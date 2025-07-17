# gemini-chatbot.py
import argparse
from clients.api_client import ApiClient
from tools.weather_tool import get_current_temperature

MODEL = "gemini-2.0-flash-lite"

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

    print(f"Gemini Chatbot d[o_0]b (Client: {client_type}, type 'exit' to quit)")
    print("=" * 40)

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        client.generate_content(user_input)

        function_call = client.get_function_call()
        if function_call:
            result = get_current_temperature(**function_call["arguments"])
            chatbot_message = f"""
                I am going to call {function_call['name']} function
                Function description: {function_call['description']}
                {("-" * 45)}
                Function arguments: {function_call['arguments']}
                {("-" * 45)}
                Function execution result: {result}
            """
        else:
            text_response = client.get_text_response()
            chatbot_message = f"""
                No function call found in the response.
                {("-" * 45)}
                Model response: {text_response}
            """

        msg_lines = chatbot_message.splitlines()
        trimmed_msg = [line.lstrip() for line in msg_lines]
        trimmed_chatbot_message = '\n'.join(trimmed_msg)
        print(f"d[o_0]b: {trimmed_chatbot_message}")


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
