# 🧠 de.ci.phe.red.lab : AI CLI User Manual

Welcome to **cryptos**, the official AI command-line interface for de.ci.phe.red.lab. This tool gives you direct access to powerful Large Language Models (LLMs) running on our central lab server, right from your local terminal.

You can use the AI to generate code, answer research questions, or even autonomously execute terminal commands and write code files on your machine.

---

## 🚀 1. Installation

You do not need to install massive AI models on your own machine. To install the lightweight client, simply open your terminal and run:

```bash
curl -s http://10.10.1.226:9000/install.sh | sudo bash
```

This will download and install the `cryptos` command to your system.

---

## 💻 2. Using the CLI

To start the interface, simply type:

```bash
cryptos
```

Upon launching, the CLI will ask you to select an AI model. Once selected, you can chat with the AI just like you would with ChatGPT.

### 🛠️ Agent Mode (Autonomous Actions)
If you ask the AI to write a file or execute a bash command (e.g., *"create a python script that prints hello world"*), the AI will autonomously attempt to do so.

**Safety First:** The system will *always* pause and ask for your permission `[Y/n]` before actually modifying your files or running a command. If the AI suggests a dangerous command, simply type `n` to reject it.

### 🔄 Changing Models
If you want to switch to a different AI model in the middle of a conversation, simply type:

```text
/model
```
The CLI will clear your chat history (to prevent context errors) and instantly switch to the new model you select.

### 🚪 Exiting
To close the session, simply type:
```text
exit
```

---

## 📡 3. Updating the CLI

The administration team will periodically push new features to the CLI. Every time you launch `cryptos`, it will silently check the lab server for updates.

If an update is available, you will see a bright yellow banner at the top of your screen. To install the update, simply run this command from your normal bash terminal:

```bash
cryptos update
```

---

## 🤖 4. Available Models

When you launch the CLI, you can choose from various models hosted on our server. Some models support autonomous tools (file writing/command execution), while others are for conversation only.

- **qwen3.5:latest** - *Recommended for Coding & Tools.* Best for autonomous agent tasks, executing tools, and writing code.
- **gemma4:e4b** - *Fast & Lightweight.* Good for quick research tasks and answers.
- **deepseek-r1:latest** - *Deep Reasoning.* Excellent for complex logic and math.
- **llama3:latest** - *General Chat.* Great for general conversation, writing, and brainstorming. *(Note: This model does not support autonomous tools).*

## 🗑️ 5. Uninstall & Reinstall

If you ever need to completely remove `cryptos` from your machine, simply run:

```bash
cryptos uninstall
```

To reinstall it fresh, just run the original installation command again:
```bash
curl -s http://10.10.1.226:9000/install.sh | sudo bash
```

---
*If you experience connection errors, ensure you are connected to the internal lab network.*
