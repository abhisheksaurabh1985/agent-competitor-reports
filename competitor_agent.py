# Gen AI Agent for Competitor Content Review and Report Generation
# Dependencies: pip install langchain langchain-community langchainhub duckduckgo-search ollama schedule requests
# Setup: Ollama installed with `ollama pull mistral`

import os
import schedule
import time
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.llms import Ollama
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Define competitors
COMPETITORS = ["Cubenergy", "Pixii", "Ampere Energy", "Ampowr"]

# Step 1: Define Tools
web_search_tool = DuckDuckGoSearchResults(
    name="web_search",
    description="Search the web for recent news, updates, or content about competitors."
)

tools = [web_search_tool]

# Step 2: Initialize LLM
llm = Ollama(model="mistral", temperature=0.3)  # Lower temperature for stricter adherence

# Step 3: Define Report Generation Chain

# The template expects two inputs: a competitor (e.g., "Cubenergy") and content (e.g., search results or news about the competitor).
# When the template is rendered, {competitor} and {content} will be replaced with actual values.

report_prompt = PromptTemplate(
    input_variables=["competitor", "content"],
    template="""
    You are an AI analyst reviewing competitor content for energy optimization companies.
    Competitor: {competitor}
    Raw Content: {content}
    
    Generate a concise report including:
    - Key updates or news.
    - Product developments (e.g., BESS, EMS).
    - Market strategies or partnerships.
    - Potential threats or opportunities for our startup.
    - Summary insights.
    
    Keep the report professional and under 500 words.
    """
)

report_chain = LLMChain(llm=llm, prompt=report_prompt)

# Step 4: Custom ReAct Prompt to Enforce Structure
react_prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    template="""
    Answer the question below using the provided tools if needed. Follow this format strictly:
    - Thought: Explain your reasoning.
    - Action: [tool_name] [input] (if using a tool, else skip)
    - Observation: (if tool used, describe results, else skip)
    - Final Answer: Your final response (only when complete).

    Tools available: {tool_names}
    Tool descriptions: {tools}
    Question: {input}
    Scratchpad: {agent_scratchpad}
    """
)

# Step 5: Define Agent
agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,  # Increased for robustness
    return_intermediate_steps=True  # For debugging
)

# Step 6: Function to Review and Generate Reports
def review_competitors():
    print("Starting competitor review...")
    reports = {}
    
    for competitor in COMPETITORS:
        print(f"Processing {competitor}...")
        query = f"Recent news and updates on {competitor} energy company 2025"
        try:
            # Gather content using agent
            result = agent_executor.invoke({"input": f"Gather recent content about {competitor}: {query}"})
            content = result.get("output", "No content retrieved.")  # Fallback if output missing
            
            # Generate report
            report = report_chain.run(competitor=competitor, content=content)
            reports[competitor] = report
            print(f"Report for {competitor}:\n{report}\n")
        except Exception as e:
            print(f"Error processing {competitor}: {str(e)}")
            reports[competitor] = f"Error: Unable to generate report due to {str(e)}"
    
    # Save reports to file
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(f"competitor-reports/report_{timestamp}.txt", "w") as f:
        f.write(f"--- Reports on {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for comp, rep in reports.items():
            f.write(f"{comp}:\n{rep}\n\n")
    # with open("competitor_reports.txt", "a") as f:
    #     f.write(f"\n--- Reports on {timestamp} ---\n")
    #     for comp, rep in reports.items():
    #         f.write(f"{comp}:\n{rep}\n\n")
    
    print("Review complete. Reports saved to competitor_reports.txt")

# Step 7: Configurable Periodicity
def start_agent(periodicity='daily'):
    """
    Start scheduling based on periodicity.
    Options: 'daily', 'weekly', 'monthly', or integer seconds (e.g., 60).
    """
    if periodicity == 'daily':
        schedule.every().day.at("09:00").do(review_competitors)
    elif periodicity == 'weekly':
        schedule.every().monday.at("09:00").do(review_competitors)
    elif periodicity == 'monthly':
        schedule.every(30).days.do(review_competitors)
    elif isinstance(periodicity, int):
        schedule.every(periodicity).seconds.do(review_competitors)
    else:
        raise ValueError("Invalid periodicity. Use 'daily', 'weekly', 'monthly', or integer seconds.")
    
    print(f"Agent scheduled to run {periodicity}.")
    while True:
        schedule.run_pending()
        time.sleep(1)

# Run the agent
if __name__ == "__main__":
    # Ensure competitor-reports directory exists
    os.makedirs("competitor-reports", exist_ok=True)

    start_agent(periodicity=60)  # Every 60 seconds for testing; change to 'daily' for production