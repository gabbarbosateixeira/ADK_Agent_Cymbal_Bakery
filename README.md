# 🤖 Cymbal Catering Agent: ADK & Agent Runtime Deployment

This repository demonstrates how to build and deploy an enterprise-grade AI assistant utilizing the **Google Agent Development Kit (ADK)** and the **Agent Runtime (Reasoning Engine)**.

The agent leverages your custom **Model Context Protocol (MCP)** server, securely registered in Google Cloud's **Agent Registry**. This unifies your backend tools under a single governance point, allowing Gemini to invoke custom databases and CRM APIs with zero manual API client coding.

---

## 🛠️ Key Features
* **Google ADK Integration:** Built using the official open-source framework for enterprise-ready AI agents.
* **Unified Tool Management:** Connects directly to a secure, registered MCP server via `AgentRegistry`.
* **Zero Trust Integration:** Operates securely using least-privilege IAM service accounts.
* **Human-in-the-Loop Safeguards:** Demonstrates how to toggle runtime user confirmations.

---

## 💡 Deep Dive: Why Use MCP & the Agent Registry with Google ADK?

In traditional AI agent development, connecting a LLM to external transactional databases or CRM systems requires manually writing, testing, and maintaining complex custom API client wrappers. 

This project bypasses that friction entirely by combining **Model Context Protocol (MCP)** with **Google's Agent Registry** and the **Agent Development Kit (ADK)**. 

### The Automated Bridge: `AgentRegistry` & `McpToolset`
In the codebase (`agent.py`), the following mechanism handles tool integration dynamically:
```python
mcp_toolset = registry.get_mcp_toolset(
    f"projects/{PROJECT_ID}/locations/us-central1/mcpServers/{MCP_SERVER_NAME}"
)
