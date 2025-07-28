.DEFAULT_GOAL := help
CHATBOT_APP := multi-model-chatbot.py

RUN_GENAI := @uv run --with 'requests' --with 'google-genai'
RUN_OPENAI := @uv run --with 'requests' --with 'openai'

.PHONY: help gemini-genai gemini-openai gemma-openai clean

# Colors for help text
green := \033[36m
white := \033[0m

help: ## Prints help for targets with comments.
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "$(green)%-30s$(white) %s\n", $$1, $$2}'

gemini-genai: ## Run google-genai library implementation with the gemini model.
	$(RUN_GENAI) $(CHATBOT_APP) --client gemini-genai

gemini-openai: ## Run openai library implementation with the gemini model.
	$(RUN_OPENAI) $(CHATBOT_APP) --client gemini-openai

gemma-openai: ## Run openai library implementation with the gemma3 model via ollama.
	$(RUN_OPENAI) $(CHATBOT_APP) --client gemma-openai --model gemma3:1b

clean: ## Remove python cache files.
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete
