# 03_crewai_research_team.py

import os
from dotenv import load_dotenv

# --- CrewAI Imports ---
from crewai import Agent, Task, Crew, Process, LLM

# --- Tool Imports ---
from langchain_tavily import TavilySearch
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# --- Load Environment Variables ---
# This will load the GOOGLE_API_KEY and TAVILY_API_KEY from your .env file
load_dotenv()
print("--- Starting CrewAI Research Team ---")

# Check if the necessary API keys are available
if "GOOGLE_API_KEY" not in os.environ or "TAVILY_API_KEY" not in os.environ:
    print("ERROR: Make sure GOOGLE_API_KEY and TAVILY_API_KEY are set in your .env file.")
    exit()
else:
    print("API keys loaded successfully.")

# Configure the LLM to use Google's Gemini
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"]
)

# Create a custom tool wrapper for Tavily
class TavilySearchInput(BaseModel):
    query: str = Field(description="Search query to find information")

class TavilySearchTool(BaseTool):
    name: str = "tavily_search"
    description: str = "Search the web for current information using Tavily"
    args_schema: Type[BaseModel] = TavilySearchInput
    
    def _run(self, query: str) -> str:
        tavily = TavilySearch()
        results = tavily.run(query)
        return results

# --- 1. Define the Tools for the Crew ---
# For this crew, our only tool is the Tavily web search.
search_tool = TavilySearchTool()
print("Tools initialized.")

# --- 2. Define the Agents (Your Team Members) ---

# Agent 1: The Researcher
researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover groundbreaking technologies and trends in AI for 2025',
  backstory="""You work at a leading tech think tank.
  Your expertise lies in identifying emerging trends by searching the web
  and providing concise, factual information.""",
  verbose=True, # Shows the agent's thought process
  allow_delegation=False, # This agent works alone on its tasks
  tools=[search_tool], # Assign the search tool to this agent
  llm=llm # Use the configured LLM
)

# Agent 2: The Writer
writer = Agent(
  role='Tech Content Strategist',
  goal='Craft compelling content on tech advancements',
  backstory="""You are a renowned Tech Content Strategist, known for your insightful
  and engaging articles. You can transform complex technical concepts into
  easy-to-understand narratives.""",
  verbose=True,
  allow_delegation=False,
  # This agent has no tools, its skill is writing.
  llm=llm # Use the configured LLM
)
print("Agents defined.")


# --- 3. Define the Tasks (The Work Assignments) ---

# Task 1: Research the topic
research_task = Task(
  description="""Conduct a comprehensive analysis of the latest advancements in AI in 2025.
  Identify the top 3-5 key trends, any breakthrough technologies, and their potential industry impacts.
  Compile your findings into a structured report.""",
  expected_output='A bullet-pointed list detailing the top 3-5 AI advancements of 2025.',
  agent=researcher # Assign this task to the researcher agent
)

# Task 2: Write an article based on the research
writing_task = Task(
  description="""Using the research analysis provided, write a compelling blog post.
  The post should be engaging, easy to understand for a non-technical audience, and have a positive tone.
  Make sure to credit the research findings in your post.""",
  expected_output='A 4-paragraph blog post titled "The Future is Now: Key AI Trends of 2025".',
  agent=writer, # Assign this task to the writer agent
  context=[research_task] # IMPORTANT: This tells the writer to use the output from the research task
)
print("Tasks defined.")

# --- 4. Assemble the Crew and Define the Process ---

my_crew = Crew(
  agents=[researcher, writer],
  tasks=[research_task, writing_task],
  process=Process.sequential, # The tasks will be executed one after another
  verbose=True # Shows all inner workings of the crew
)
print("Crew assembled. Kicking off the mission...")
print("-" * 50)

# --- 5. Kick Off the Mission! ---

# The .kickoff() method starts the process and returns the final output from the last task.
result = my_crew.kickoff()

print("\n\n" + "-"*50)
print("MISSION COMPLETE! Here is the final result:")
print(result)
