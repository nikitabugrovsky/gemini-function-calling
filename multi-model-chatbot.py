# multi-model-chatbot.py
import argparse
import json

from clients.api_client import ApiClient
from tools.weather_tool import get_current_weather

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text

class Color:
    """Class to hold prompt_toolkit-compatible color names."""
    GREEN = "ansigreen"
    YELLOW = "ansiyellow"
    BLUE = "ansiblue"
    RED = "ansired"
    BOLD = "bold"

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

def main(client_type: str, model_type: str) -> None:
    """Executes the chatbot flow using the selected API client."""
    client = get_api_client(client_type, model_type)

    header = FormattedText([
        (Color.BOLD, 'Multi-model Chatbot '),
        (f'{Color.GREEN} {Color.BOLD}', 'd[o_0]b'),
        (Color.BOLD, f' (Client: {client_type}, model: {model_type}, type '),
        (f'{Color.RED} {Color.BOLD}', "'exit' "),
        (Color.BOLD, 'or press '),
        (f'{Color.RED} {Color.BOLD}', "'Ctrl + D' "),
        (Color.BOLD, 'to quit)')
    ])
    print_formatted_text(header)
    print_formatted_text(FormattedText([(Color.BOLD, "=" * 60)]))

    while True:
        try:
            prompt_text = FormattedText([(f'{Color.YELLOW} {Color.BOLD}', 'You: ')])
            user_input = prompt(prompt_text).strip()

            if user_input.lower() in ("exit", "quit"):
                break

            client.generate_content(user_input, function_execution_result=None)

            function_call = client.get_function_call()
            if function_call:
                thinking_msg = FormattedText([
                    (f'{Color.GREEN} {Color.BOLD}', 'd[o_0]b'),
                    (Color.BLUE, '[Tool: None]: '),
                    ('', f"I am gonna call {function_call['name']} tool with arguments: {json.dumps(function_call['arguments'])}")
                ])
                print_formatted_text(thinking_msg)

                result = get_current_weather(**function_call["arguments"])
                client.generate_content(user_input=None, function_execution_result=result)
                chatbot_message = client.get_text_response()

                bot_msg = FormattedText([
                    (f'{Color.GREEN} {Color.BOLD}', 'd[o_0]b'),
                    (Color.BLUE, f'[Tool: {function_call["name"]}]: '),
                    ('', f'{chatbot_message.strip()}')
                ])
                print_formatted_text(bot_msg)
            else:
                text_response = client.get_text_response()
                bot_msg = FormattedText([
                    (f'{Color.GREEN} {Color.BOLD}', 'd[o_0]b'),
                    (Color.BLUE, '[Tool: None]: '),
                    ('', f'{text_response.strip()}')
                ])
                print_formatted_text(bot_msg)

        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            break

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
