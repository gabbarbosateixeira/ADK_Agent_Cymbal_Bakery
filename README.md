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


#### Under the Hood:
1. **Dynamic Resolution:** Rather than hardcoding a server URL or API endpoints, the ADK uses the `AgentRegistry` client to dynamically query the Central Registry at runtime. 
2. **Schema & Binding Resolution:** It automatically fetches and parses the server's registered JSON toolspec schema, learning the exact parameters, names, and descriptions of all 7 catering/CRM tools.
3. **Managed Authentication:** The registry client automatically resolves the required security bindings, credentials, and access tokens needed to communicate with your backend.

#### Why This is Architectural Gold:
* **No Hardcoded APIs:** It acts as an **automated, managed bridge** between your AI agent and external systems. If you add, delete, or rename tools on your MCP server, you do not need to rewrite your agent's code. Simply refresh the registry, and the agent adapts instantly.
* **Robust Client-Side Validation:** Gemini checks and validates arguments against the registry-cached JSON schema *before* making a request. This saves compute resources and blocks malformed payloads from hitting your backend databases.
* **Build Once, Reuse Everywhere:** The Registry acts as a single, central folder/catalog in your project. This exact toolset is now reusable across multiple agents, playbooks, or pipelines with zero code replication.

---

## 📋 Prerequisites

Before deploying the agent, ensure the following prerequisites are met:
1. **MCP Server Deployed:** Your custom MCP server must be deployed on Cloud Run and reachable (See the [Cymbal Catering MCP Server Project](https://github.com/gabbarbosateixeira/cymbal-catering-mcp)).
2. **MCP Registered:** The server must be registered in your GCP project's **Agent Registry** (Location: `us-central1`).
3. **Google Cloud SDK:** The `gcloud` CLI tool must be installed and authenticated to your project.
4. **Google ADK installed:** Ensure you have the `adk` command line tool available.

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Clone the Repository
Create a directory for your agent project and clone this repository:
```bash
mkdir -p cymbal-agent && cd cymbal-agent
git clone https://github.com/gabbarbosateixeira/cymbal-catering-mcp.git .
```

### Step 2: Install Dependencies
Install the required Google ADK packages and runtime dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root of your project directory:
```env
GOOGLE_CLOUD_PROJECT=gemini-enterprise-demo-502515
MCP_SERVER_NAME=agentregistry-00000000-0000-0000-5dcb-996f7dd8be9d
```

### Step 4: Validate Locally
Run a quick import check to verify that all Python packages and local files load without errors:
```bash
python3 -c "import agent"
```

---

## 🔐 Step 5: Configure IAM & Permissions

For your deployed Agent to read toolspecs from the Registry and invoke your Cloud Run MCP service, you must assign the correct IAM bindings to the respective Google Service Accounts. 

Run the following script in your **Cloud Shell** to automate this configuration (all broken lines from standard OCR have been cleanly resolved):

```bash
# Define project variables
export PROJECT_ID="gemini-enterprise-demo-502515"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 1. Authorize Reasoning Engine Service Agent
# Grants permission to read tool definitions and schemas stored in Agent Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/agentregistry.viewer"

# 2. Authorize Default Compute Service Account
# Ensures fallback execution environments can fetch tool metadata from Agent Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/agentregistry.viewer"

# 3. Authorize Discovery Engine Service Agent
# Allows Gemini Enterprise & Vertex AI Playgrounds to inspect and render MCP toolcards
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/agentregistry.viewer"
```

### 🔑 Security Role Reference:
* **`roles/agentregistry.viewer`**: Allows service agents to read schemas, metadata, and configuration parameters of the registered MCP tools.
* **`roles/run.invoker`**: Required on the target Cloud Run service (`cymbal-mcp`) so the Reasoning Engine runtime can send authenticated POST requests to trigger tools.

---

## 🔓 Step 6: Demo Mode - Bypassing Sandbox Restrictions

If you are running this demo in an **Argolis Sandbox**, Domain Restricted Sharing (DRS) will prevent public, unauthenticated access. Use these toggles to quickly open access for your demo and restore them immediately afterward.

### 🟢 Disable Domain Restrictions (Pre-Demo Setup)
```bash
# A. Apply project-level override to break org policy inheritance
gcloud resource-manager org-policies set-policy /dev/stdin --project=gemini-enterprise-demo-502515 <<EOF
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allValues: ALLOW
  inheritFromParent: false
EOF

# B. Grant unauthenticated invoker rights to your Cloud Run service
gcloud run services add-iam-policy-binding cymbal-mcp \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### 🔴 Restore Domain Restrictions (Post-Demo Cleanup)
```bash
# A. Revoke unauthenticated public access
gcloud run services remove-iam-policy-binding cymbal-mcp \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# B. Remove the project-level override to re-enable strict org inheritance
gcloud resource-manager org-policies delete constraints/iam.allowedPolicyMemberDomains --project=gemini-enterprise-demo-502515
```

---

## 🚀 Step 7: Deploy Your Agent to Agent Runtime

Deploy your configured agent to the Vertex AI Reasoning Engine:
```bash
# Authenticate application default credentials
gcloud auth application-default login

# Deploy using the ADK CLI
adk deploy agent_engine . --region=us-central1
```

Once deployment is complete, the console will print your unique **Agent Endpoint Address**. You can monitor and access this deployment directly in the Cloud Console under **Agent Platform** -> **Deployments**.

---

## 🎯 Testing & Playground

Once deployed, navigate to the **Vertex AI Agent Studio Playground** or the **Gemini Enterprise console** to interact with your agent.

* **Example User Queries:**
  * *"How many new leads do we have in our CRM?"*
  * *"Add a VIP Private client named Alice Smith (alice@example.com) from Gamma LLC."*
  * *"Place a confirmed catering order for Gamma LLC's anniversary party on September 5, 2026."*

---

