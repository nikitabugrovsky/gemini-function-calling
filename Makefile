.DEFAULT_GOAL := help

.PHONY: help

green := \033[36m
white := \033[0m

help: ## Prints help for targets with comments.
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "$(green)%-30s$(white) %s\n", $$1, $$2}'

gemini-genai: ## Run google-genai library implementation.
	uv run gemini-genai.py

gemini-openai: ## Run openai library implementation.
	uv run gemini-openai.py
