
# How to get started?

Steps below asuume that a Python virtual environment is active. If not, install Python virtual environment and activate it. 

1. Install Dependencies: Run `pip install langchain langchain-community langchainhub duckduckgo-search ollama schedule requests`.
2. Setup Ollama: Download from https://ollama.com, then `ollama pull mistral`.
3. Execute the Script: Save as `competitor_agent.py` and run `python competitor_agent.py`. It will schedule and run reviews based on your configured periodicity.
4. Testing: Use `start_agent(60)` to run every minute for quick tests. 