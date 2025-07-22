.DEFAULT_GOAL := help
CHATBOT_APP := multi-model-chatbot.py

.PHONY: help

green := \033[36m
white := \033[0m

help: ## Prints help for targets with comments.
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "$(green)%-30s$(white) %s\n", $$1, $$2}'

gemini-genai: ## Run google-genai library implementation with the gemini model.
	@uv run --with 'requests' --with 'google-genai' $(CHATBOT_APP) --client gemini-genai

gemini-openai: ## Run openai library implementation with the gemini model.
	@uv run --with 'requests' --with 'openai' $(CHATBOT_APP) --client gemini-openai

gemma-openai: ## Run openai library implementation with the gemma3 model via ollama.
	@uv run --with 'requests' --with 'openai' $(CHATBOT_APP) --client gemma-openai --model gemma3:1b
