# de.ci.phe.red.lab : AI CLI (cryptos)
## Project Architecture & Implementation Documentation

### 1. Project Overview
`cryptos` is a custom, centralized AI command-line interface designed specifically for **de.ci.phe.red.lab**. It provides lab members with direct access to advanced Large Language Models (LLMs) from their personal workstations without requiring massive local GPU compute. The CLI is fully autonomous, capable of executing bash commands and writing code files directly to the user's local machine to solve complex engineering and research tasks.

### 2. System Architecture
The system relies on a highly efficient **Client-Server Architecture**:
*   **Host Server (Admin Node):** Runs `Ollama` exposed on port `11434` to serve the heavy LLMs (Qwen3.5, Llama3, Deepseek, Gemma) over the local lab network (`10.10.1.226`). It also runs a simple Python HTTP server on port `9000` to serve the CLI script (`lab-cli.py`) and OTA updates (`version.txt`). This server is maintained by running:
    ```bash
    python3 -m http.server 9000 --directory /home/crypto_nn/lab-ai-cli
    ```
*   **Client Node (Lab Members):** A lightweight Python script (`/usr/local/bin/cryptos`) that connects to the host server via REST API. It requires zero local AI dependencies—only the `requests` and `rich` Python libraries for network transport and the UI.

### 3. Core Features & Engineering
#### A. Dynamic Model Switching
The CLI queries the host server's `/api/tags` endpoint on startup to dynamically list all available models. If the admin installs a new model on the host server, it instantly appears as an option for all lab members without requiring a client update.

#### B. Autonomous Agentic Capabilities (Tool Calling)
When compatible models (like `qwen3.5:latest`) are selected, the CLI injects a system prompt instructing the AI to use specific JSON-formatted tools:
1.  **`execute_command`**: Allows the AI to autonomously run bash commands, check system state, read directories, and install dependencies.
2.  **`write_file`**: Allows the AI to generate, refactor, and save code files to the disk.

#### C. Human-in-the-Loop Safety Intercept
Because the AI can autonomously run terminal commands, safety is paramount. The script intercepts every single tool call requested by the AI and pauses the execution loop. It prompts the human user for explicit approval (`[Y/n]`) before passing the command to the OS or modifying the filesystem, preventing accidental destructive actions.

#### D. Over-The-Air (OTA) Updates
The client script checks `http://10.10.1.226:9000/version.txt` on startup. If a newer version is available, it renders a yellow alert banner to the user. Users simply type `cryptos update` to trigger an internal function that fetches the latest `lab-cli.py` and overwrites their local binary in `/usr/local/bin/cryptos`.

#### E. Intelligent Fallback Logic
If a user selects a model that does not natively support tool calling (such as standard `llama3`), the CLI automatically catches the resulting `400 Bad Request` from the Ollama server, strips the tool definitions from the payload, and seamlessly retries the request as a standard conversational chatbot.

### 4. Implementation Details
The CLI was built using standard Python and relies on the following execution loop:
1.  **Bootstrap & Branding:** Initializes the `rich` library to render the custom `de.ci.phe.red.lab` modern ASCII logo and UI panels, adapting dynamically to terminal width.
2.  **Conversation Loop:** Captures user input and appends it to a running `messages` array to maintain multi-turn chat context history.
3.  **API Dispatch:** Sends the `messages` array and the `TOOLS` JSON schema to the Ollama endpoint via a synchronous HTTP POST request.
4.  **Action Parsing:** Inspects the response object for the `"tool_calls"` array. If found, it parses the arguments, routes them to local Python functions (using `subprocess` for bash, and standard I/O for files), feeds the command's `stdout/stderr` result back into the `messages` array, and re-queries the model so the AI can interpret the system output.
