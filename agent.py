import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.integrations.agent_registry import AgentRegistry

# Load configuration variables from .env
load_dotenv(".env")

# Set regional variables for GenAI Client
os.environ["GOOGLE_CLOUD_LOCATION"] = "us"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME")

# Connect to Agent Registry
registry = AgentRegistry(project_id=PROJECT_ID, location="us-central1")

# Fetch MCP Toolset from the Agent Registry
mcp_toolset = registry.get_mcp_toolset(
    f"projects/{PROJECT_ID}/locations/us-central1/mcpServers/{MCP_SERVER_NAME}"
)

# Configure Gemini Model Client
gemini_model = Gemini(
    model="gemini-3.6-flash",
    retry_options=types.HttpRetryOptions(attempts=3)
)

# Initialize the Root Catering & CRM Agent
root_agent = Agent(
    name="cymbal_bakery_agent",
    description=(
        "You are the expert Catering & CRM Assistant for Cymbal Bakery. "
        "When helping with orders, always pay attention to critical details like event dates, "
        "guest counts, order status (Pending, Confirmed, In Prep), and dietary restrictions. "
        "If a user asks to create or update an order, verify you have all necessary details "
        "(Client, Date, Items, Guests) before executing the tool. Be professional, concise, and helpful."
    ),
    model=gemini_model,
    tools=[mcp_toolset],
)
