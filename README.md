# Multi-LLM Fullstack LangGraph Quickstart

This project demonstrates a fullstack application using a React frontend and a LangGraph-powered backend agent. The agent is designed to perform comprehensive research on a user's query by dynamically generating search terms, querying the web using various search engines, reflecting on the results to identify knowledge gaps, and iteratively refining its search until it can provide a well-supported answer with citations. This application serves as an example of building research-augmented conversational AI using LangGraph and multiple LLM providers including DeepSeek, 智谱AI, OpenAI, and custom models.

<img src="./app.png" title="Gemini Fullstack LangGraph" alt="Gemini Fullstack LangGraph" width="90%">

## Features

- 💬 Fullstack application with a React frontend and LangGraph backend.
- 🧠 Powered by a LangGraph agent for advanced research and conversational AI.
- 🔍 Dynamic search query generation using Google Gemini models.
- 🌐 Integrated web research via Google Search API.
- 📚 **RAG Integration**: Seamlessly integrate with RAGFlow for private knowledge base retrieval.
- 🤔 Reflective reasoning to identify knowledge gaps and refine searches.
- 📄 Generates answers with citations from gathered sources.
- 🔄 Hot-reloading for both frontend and backend during development.

## Project Structure

The project is divided into two main directories:

-   `frontend/`: Contains the React application built with Vite.
-   `backend/`: Contains the LangGraph/FastAPI application, including the research agent logic.

## Getting Started: Development and Local Testing

Follow these steps to get the application running locally for development and testing.

**1. Prerequisites:**

-   Node.js and npm (or yarn/pnpm)
-   Python 3.11+
-   **LLM API Key**: The backend agent requires at least one LLM API key. Choose from:
    - DeepSeek: `DEEPSEEK_API_KEY`
    - 智谱AI: `ZHIPUAI_API_KEY`
    - 阿里千问: `QWEN_API_KEY`
    - OpenAI: `OPENAI_API_KEY`
    - Custom model: `LLM_API_KEY` + `LLM_BASE_URL`
    1.  Navigate to the `backend/` directory.
    2.  Create a file named `.env` with the following configuration:
    ```bash
    # LLM Configuration (choose one or more)
    # DeepSeek
    DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"
    
    # 智谱AI
    # ZHIPUAI_API_KEY="YOUR_ZHIPUAI_API_KEY"
    
    # 阿里千问
    # QWEN_API_KEY="YOUR_QWEN_API_KEY"
    
    # OpenAI
    # OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    
    # Custom OpenAI-compatible API
    # LLM_API_KEY="YOUR_CUSTOM_API_KEY"
    # LLM_BASE_URL="https://your-custom-api.com"
    # LLM_MODEL_NAME="your-model-name"
    

    
    # Optional: RAG Configuration
    # Uncomment and configure the following to enable RAG with RAGFlow:
    # RAG_PROVIDER="ragflow"
    # RAGFLOW_API_URL="http://localhost:9380"
    # RAGFLOW_API_KEY="ragflow-xxx"
    ```

**2. Install Dependencies:**

**Backend:**

```bash
cd backend
pip install .
```

**Frontend:**

```bash
cd frontend
npm install
```

**3. Run Development Servers:**

**Backend & Frontend:**

```bash
make dev
```
This will run the backend and frontend development servers.    Open your browser and navigate to the frontend development server URL (e.g., `http://localhost:3000/app`).

_Alternatively, you can run the backend and frontend development servers separately. For the backend, open a terminal in the `backend/` directory and run `python start_server.py`. The backend API will be available at `http://127.0.0.1:2024`. It will also open a browser window to the LangGraph UI. For the frontend, open a terminal in the `frontend/` directory and run `npm run dev`. The frontend will be available at `http://localhost:3000`._

## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

<img src="./agent.png" title="Agent Flow" alt="Agent Flow" width="50%">

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using your chosen LLM (DeepSeek, 智谱AI, 阿里千问, OpenAI, or custom model).
2.  **RAG Retrieval (Optional):** If RAG resources are selected, the agent first retrieves relevant documents from your RAGFlow knowledge base.
3.  **Web Research:** For each query, it uses your chosen LLM with the configured search engine (Tavily, Serper, Google, or DuckDuckGo) to find relevant web pages.
4.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the search results to determine if the information is sufficient or if there are knowledge gaps using your chosen LLM.
5.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the web research and reflection steps (up to a configured maximum number of loops).
6.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer, including citations from both RAG documents and web sources, using your chosen LLM.

## RAG Integration

This project now includes RAG (Retrieval-Augmented Generation) integration with RAGFlow, allowing you to combine web research with private knowledge base retrieval.

### RAG Features

- **🔗 RAGFlow Integration**: Connect to your RAGFlow instance to access private documents and knowledge bases.
- **📂 Resource Selection**: Choose specific datasets or documents from your RAGFlow knowledge base.
- **🔄 Hybrid Research**: Combine RAG retrieval with web search for comprehensive answers.
- **📊 Smart Routing**: The agent intelligently decides when to use RAG vs. web search based on available resources.

### Setting Up RAG

1. **Install and Configure RAGFlow**:
   - Follow the [RAGFlow installation guide](https://ragflow.io/docs/dev/) to set up your RAGFlow instance.
   - Create knowledge bases and upload your documents.
   - Obtain your RAGFlow API key from the settings page.

2. **Configure Environment Variables**:
   ```bash
   # Enable RAG by setting the provider
   RAG_PROVIDER="ragflow"
   
   # RAGFlow connection details
   RAGFLOW_API_URL="http://localhost:9380"  # Your RAGFlow server URL
   RAGFLOW_API_KEY="ragflow-xxx"           # Your RAGFlow API key
   ```

3. **Using RAG in the Application**:
   - When RAG is enabled, you'll see a "Add RAG Resources" button in the input form.
   - Click to browse and select datasets from your RAGFlow knowledge base.
   - Selected resources will be used for retrieval before web research begins.
   - The agent will show RAG retrieval progress in the activity timeline.

### How RAG Works in the Agent

When RAG resources are selected:

1. **RAG Retrieval**: The agent first queries your selected RAGFlow datasets for relevant information.
2. **Context Enhancement**: Retrieved documents are added to the agent's context.
3. **Web Research**: The agent then performs web research to fill any remaining knowledge gaps.
4. **Answer Synthesis**: Both RAG content and web research results are combined for the final answer.

## CLI Example

For quick one-off questions you can execute the agent from the command line. The
script `backend/examples/cli_research.py` runs the LangGraph agent and prints the
final answer:

```bash
cd backend
python examples/cli_research.py "What are the latest trends in renewable energy?"
```


## Deployment

In production, the backend server serves the optimized static frontend build. LangGraph requires a Redis instance and a Postgres database. Redis is used as a pub-sub broker to enable streaming real time output from background runs. Postgres is used to store assistants, threads, runs, persist thread state and long term memory, and to manage the state of the background task queue with 'exactly once' semantics. For more details on how to deploy the backend server, take a look at the [LangGraph Documentation](https://langchain-ai.github.io/langgraph/concepts/deployment_options/). Below is an example of how to build a Docker image that includes the optimized frontend build and the backend server and run it via `docker-compose`.

_Note: For the docker-compose.yml example you need a LangSmith API key, you can get one from [LangSmith](https://smith.langchain.com/settings)._

_Note: If you are not running the docker-compose.yml example or exposing the backend server to the public internet, you should update the `apiUrl` in the `frontend/src/App.tsx` file to your host. Currently the `apiUrl` is set to `http://localhost:8123` for docker-compose or `http://localhost:2024` for development._

**1. Build the Docker Image:**

   Run the following command from the **project root directory**:
   ```bash
   docker build -t gemini-fullstack-langgraph -f Dockerfile .
   ```
**2. Run the Production Server:**

   ```bash
   # At least one LLM API key is required
   DEEPSEEK_API_KEY=<your_deepseek_api_key> \
   LANGSMITH_API_KEY=<your_langsmith_api_key> \
   docker-compose up
   
   # Or use other LLM providers:
   # ZHIPUAI_API_KEY=<your_zhipuai_api_key> docker-compose up
   # QWEN_API_KEY=<your_qwen_api_key> docker-compose up
   # OPENAI_API_KEY=<your_openai_api_key> docker-compose up
   ```

Open your browser and navigate to `http://localhost:8123/app/` to see the application. The API will be available at `http://localhost:8123`.

## Technologies Used

- [React](https://reactjs.org/) (with [Vite](https://vitejs.dev/)) - For the frontend user interface.
- [Tailwind CSS](https://tailwindcss.com/) - For styling.
- [Shadcn UI](https://ui.shadcn.com/) - For components.
- [LangGraph](https://github.com/langchain-ai/langgraph) - For building the backend research agent.
- **Multiple LLM Providers**:
  - [DeepSeek](https://www.deepseek.com/) - Fast and cost-effective LLM
  - [智谱AI](https://www.zhipuai.cn/) - Chinese LLM provider
  - [阿里千问](https://tongyi.aliyun.com/) - Alibaba's powerful LLM
  - [OpenAI](https://openai.com/) - Industry-leading LLM
  - Custom OpenAI-compatible APIs
- **Search Engines**:
  - [Tavily](https://tavily.com/) - AI-powered search
  - [Serper](https://serper.dev/) - Google Search API
  - [Google Custom Search](https://developers.google.com/custom-search)
  - [DuckDuckGo](https://duckduckgo.com/) - Privacy-focused search
- [RAGFlow](https://github.com/infiniflow/ragflow) - For RAG-based private knowledge base integration.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details. 
