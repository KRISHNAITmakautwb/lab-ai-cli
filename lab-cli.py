#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    import requests
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.align import Align
    import readline
except ImportError:
    print("Missing required libraries. Please run: pip install requests rich")
    sys.exit(1)

console = Console()

VERSION = "1.2.2"
OLLAMA_SERVER = "http://10.10.1.226:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:latest"

SESSION_ALLOW_ALL = False

MODEL_DESCRIPTIONS = {
    "qwen": "Best for autonomous agent tasks, executing tools, and coding.",
    "llama3": "Great for general conversation, writing, and brainstorming.",
    "deepseek-r1": "Excellent for deep reasoning, complex logic, and math.",
    "gemma": "Good for lightweight tasks, research, and quick answers."
}

# Define the "Tools" the AI is allowed to use on your machine
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a terminal bash command on the user's local machine. Use this to create directories, install packages, or check system state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write code or text directly to a file on the user's local machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to create or overwrite."
                    },
                    "content": {
                        "type": "string",
                        "description": "The code or text content to write."
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the text content of a file on the user's local machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to read."
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for information, documentation, or research.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def execute_command(command):
    global SESSION_ALLOW_ALL
    try:
        console.print(f"\n[bold yellow]⚡ Action Request:[/bold yellow] Execute command -> [cyan]{command}[/cyan]")
        if not SESSION_ALLOW_ALL:
            confirm = console.input("[bold red]Allow this command? [Enter for Yes / a for All / n for No]: [/bold red]").strip().lower()
            if confirm in ['n', 'no']:
                console.print("[dim]Action cancelled by user.[/dim]")
                return "User denied permission to execute this command."
            elif confirm in ['a', 'all']:
                SESSION_ALLOW_ALL = True
            
        console.print("[dim]Executing...[/dim]")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.stderr:
            output += f"\n{result.stderr}"
        return output if output.strip() else "Command executed successfully with no output."
    except Exception as e:
        return str(e)

def write_file(filepath, content):
    global SESSION_ALLOW_ALL
    try:
        filepath = os.path.expanduser(filepath)
        console.print(f"\n[bold yellow]⚡ Action Request:[/bold yellow] Write to file -> [cyan]{filepath}[/cyan]")
        if not SESSION_ALLOW_ALL:
            confirm = console.input("[bold red]Allow writing this file? [Enter for Yes / a for All / n for No]: [/bold red]").strip().lower()
            if confirm in ['n', 'no']:
                console.print("[dim]Action cancelled by user.[/dim]")
                return "User denied permission to write this file."
            elif confirm in ['a', 'all']:
                SESSION_ALLOW_ALL = True
            
        console.print("[dim]Writing...[/dim]")
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return str(e)

def read_file(filepath):
    global SESSION_ALLOW_ALL
    try:
        filepath = os.path.expanduser(filepath)
        console.print(f"\n[bold yellow]⚡ Action Request:[/bold yellow] Read file -> [cyan]{filepath}[/cyan]")
        if not SESSION_ALLOW_ALL:
            confirm = console.input("[bold red]Allow reading this file? [Enter for Yes / a for All / n for No]: [/bold red]").strip().lower()
            if confirm in ['n', 'no']:
                console.print("[dim]Action cancelled by user.[/dim]")
                return "User denied permission to read this file."
            elif confirm in ['a', 'all']:
                SESSION_ALLOW_ALL = True
            
        console.print("[dim]Reading...[/dim]")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()[:8000] # Limit to 8000 chars to avoid blowing up context window
    except Exception as e:
        return str(e)

def web_search(query):
    global SESSION_ALLOW_ALL
    try:
        console.print(f"\n[bold yellow]⚡ Action Request:[/bold yellow] Search the web -> [cyan]{query}[/cyan]")
        if not SESSION_ALLOW_ALL:
            confirm = console.input("[bold red]Allow this search query to be sent to the internet? [Enter for Yes / a for All / n for No]: [/bold red]").strip().lower()
            if confirm in ['n', 'no']:
                console.print("[dim]Action cancelled by user for privacy.[/dim]")
                return "User denied permission to search the web."
            elif confirm in ['a', 'all']:
                SESSION_ALLOW_ALL = True
            
        console.print("[dim]Searching the web...[/dim]")
        import re
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) lab-ai-cli/{VERSION}"}
        response = requests.get(url, params={"q": query}, headers=headers, timeout=15).text
        
        titles = re.findall(r'<h2 class="result__title">\s*<a[^>]*>(.*?)</a>', response, re.I | re.DOTALL)
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', response, re.I | re.DOTALL)
        
        results = []
        for i in range(min(5, len(titles))):
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            snippet = re.sub(r'<[^>]+>', '', snippets[i] if i < len(snippets) else '').strip()
            
            title = title.replace('&#x27;', "'").replace('&quot;', '"').replace('&amp;', '&')
            snippet = snippet.replace('&#x27;', "'").replace('&quot;', '"').replace('&amp;', '&')
            
            results.append(f"Title: {title}\nInformation: {snippet}")
            
        if not results:
            return "No search results found."
        return "\n\n".join(results)
    except Exception as e:
        return f"Web search failed: {str(e)}"

def get_available_models():
    try:
        response = requests.get("http://10.10.1.226:11434/api/tags", timeout=5)
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]
    except Exception:
        return [DEFAULT_MODEL]

def get_system_prompt():
    base_prompt = "You are an autonomous AI Agent running locally on a user's terminal. You have tools to execute bash commands, write files, read files, and search the web. CRITICAL RULE 1: NEVER ask the user for permission in chat. Just use your tools immediately. The system will automatically pause and ask the user for approval before the tool actually executes. CRITICAL RULE 2: If a file path has spaces, ALWAYS wrap the path in quotes. CRITICAL RULE 3: ONLY use tools when strictly necessary. If the user is just saying hello or having a normal conversation, DO NOT use tools (like echo). Just reply directly with text."
    
    profile_path = os.path.expanduser("~/.cryptos_profile.txt")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                user_info = f.read().strip()
            if user_info:
                base_prompt += f"\n\nHere is private information about the user and their lab research. Memorize this and use it to tailor your responses:\n{user_info}"
        except:
            pass
    return base_prompt

def main():
    global SESSION_ALLOW_ALL
    if len(sys.argv) > 1 and sys.argv[1].lower() == "update":
        print("📥 Fetching the latest version from the lab server...")
        os.system("sudo curl -s http://10.10.1.226:9000/lab-cli.py -o /usr/local/bin/cryptos")
        print("✅ Update complete! You are now on the newest version.")
        sys.exit(0)
        
    if len(sys.argv) > 1 and sys.argv[1].lower() == "uninstall":
        print("🗑️ Uninstalling cryptos CLI...")
        os.system("sudo rm -f /usr/local/bin/cryptos")
        print("✅ Uninstallation complete! The cryptos command has been removed from your system.")
        sys.exit(0)
        
    os.system("clear")
    
    models = get_available_models()
    if len(models) > 1:
        console.print(Panel("[bold red]de.ci.phe.red.[/bold red][bold white]lab : AI CLI - Select Model[/bold white]", border_style="red", expand=False))
        for i, m in enumerate(models, 1):
            desc = "General purpose AI model."
            for key, val in MODEL_DESCRIPTIONS.items():
                if key in m.lower():
                    desc = val
                    break
            console.print(f"  [bold green]{i}.[/bold green] [bold]{m}[/bold]\n     [dim]↳ {desc}[/dim]")
        choice = console.input(f"\n[bold yellow]Enter number to select model (1-{len(models)}) \\\\[default 1]: [/bold yellow]")
        try:
            selected_model = models[int(choice.strip()) - 1] if choice.strip() else models[0]
        except:
            selected_model = models[0]
    else:
        selected_model = models[0]
        
    os.system("clear")
    ascii_logo = """[bold red]
   _____  ____  __  __  ____  ______  ____   _____ 
  / ___/ / __ \\ \\ \\/ / / __ \\/_  __/ / __ \\ / ___/ 
 / /__  / /_/ /  \\  / / /_/ / / /   / /_/ / \\__ \\  
 \\___/ /_/\\_\\    /_/ / .___/ /_/    \\____/ /____/  
                    /_/                            
[/bold red]"""
    console.print(Align.center(ascii_logo))
    console.print(Align.center(f"[bold white]de.ci.phe.red.lab : AI CLI v{VERSION}[/bold white]\n"))
    
    console.print("[bold white]Tips for getting started:[/bold white]")
    console.print("1. Ask questions, edit files, or run commands autonomously.")
    console.print("2. The AI will prompt you for approval before editing your system.")
    console.print("3. Type [bold magenta]/model[/bold magenta] to switch AI models mid-conversation.")
    console.print("4. Type [bold magenta]cryptos update[/bold magenta] in your normal terminal to download new features.")
    console.print("5. Type [bold magenta]exit[/bold magenta] to close the CLI.\n")
    
    try:
        ver_resp = requests.get("http://10.10.1.226:9000/version.txt", timeout=1.5)
        latest_version = ver_resp.text.strip()
        if latest_version and latest_version != VERSION:
            update_msg = f"[bold yellow]cryptos update available! {VERSION} ➜ {latest_version}[/bold yellow]\nRun [bold white]cryptos update[/bold white] from your terminal to install it."
            console.print(Panel(update_msg, border_style="yellow", expand=False))
            console.print()
    except Exception:
        pass
    
    status_panel = f"CLI Version: v{VERSION}\nServer Connection: {OLLAMA_SERVER}\nAgent Mode: Enabled"
    console.print(Panel(status_panel, border_style="yellow", expand=False))
    console.print(f"\n[dim]~                   de.ci.phe.red.lab                 {selected_model}[/dim]")
    
    # Give the AI a system prompt instructing it to use tools
    messages = [{
        "role": "system", 
        "content": "You are an autonomous AI Agent running locally on a user's terminal. You have tools to execute bash commands and write files. CRITICAL RULE 1: NEVER ask the user for permission in chat. Just use your tools immediately. The system will automatically pause and ask the user for approval before the tool actually executes. If the user denies permission, suggest an alternative. CRITICAL RULE 2: If a file path has spaces, ALWAYS wrap the path in quotes when using execute_command."
    }]
    
    while True:
        try:
            console.print()
            user_input = console.input("[bold green]❯ You:[/bold green] ")
            
            if user_input.strip().lower() in ['exit', 'quit']:
                break
            if user_input.strip().lower() in ['change model', '/model']:
                models = get_available_models()
                console.print(Panel("[bold red]de.ci.phe.red.[/bold red][bold white]lab : AI CLI - Change Model[/bold white]", border_style="red", expand=False))
                for i, m in enumerate(models, 1):
                    desc = "General purpose AI model."
                    for key, val in MODEL_DESCRIPTIONS.items():
                        if key in m.lower():
                            desc = val
                            break
                    console.print(f"  [bold green]{i}.[/bold green] [bold]{m}[/bold]\n     [dim]↳ {desc}[/dim]")
                choice = console.input(f"\n[bold yellow]Select new model (1-{len(models)}): [/bold yellow]")
                try:
                    selected_model = models[int(choice.strip()) - 1] if choice.strip() else selected_model
                    console.print(f"[bold green]✅ Model successfully changed to {selected_model}[/bold green]")
                    
                    messages = [{
                        "role": "system", 
                        "content": get_system_prompt()
                    }]
                    SESSION_ALLOW_ALL = False
                    console.print("[dim]Note: Conversation history cleared to prevent context errors with new model.[/dim]\n")
                except:
                    console.print("[bold red]❌ Invalid selection. Model not changed.[/bold red]\n")
                continue
                
            if not user_input.strip():
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            # Agentic Loop
            while True:
                payload = {
                    "model": selected_model,
                    "messages": messages,
                    "tools": TOOLS,
                    "stream": False # Turn off streaming so it can return complete Tool payloads reliably
                }
                
                try:
                    with console.status("[bold magenta]📡 Querying de.ci.phe.red Lab server...[/bold magenta]", spinner="dots"):
                        response = requests.post(OLLAMA_SERVER, json=payload)
                        response.raise_for_status()
                        result = response.json()
                        
                    msg = result.get("message", {})
                    
                    # If the AI decides it needs to take an ACTION (Tool Call)
                    if "tool_calls" in msg and msg["tool_calls"]:
                        messages.append(msg) # Save the AI's action intent to history
                        
                        for tool_call in msg["tool_calls"]:
                            function_name = tool_call["function"]["name"]
                            args = tool_call["function"]["arguments"]
                            
                            if function_name == "execute_command":
                                tool_result = execute_command(args.get("command"))
                            elif function_name == "write_file":
                                tool_result = write_file(args.get("filepath"), args.get("content"))
                            elif function_name == "read_file":
                                tool_result = read_file(args.get("filepath"))
                            elif function_name == "web_search":
                                tool_result = web_search(args.get("query"))
                            else:
                                tool_result = f"Unknown tool: {function_name}"
                                
                            # Feed the result of the action back to the AI
                            messages.append({
                                "role": "tool",
                                "name": function_name,
                                "content": tool_result
                            })
                            
                        # Loop back up to let the AI process the tool result and respond again
                        continue
                    
                    # If the AI just wants to TALK (no tools used)
                    else:
                        content = msg.get("content", "")
                        if content:
                            console.print("\n[bold red]✨ de.ci.phe.red.lab:[/bold red]")
                            console.print(Markdown(content))
                            messages.append({"role": "assistant", "content": content})
                        break # Exit the agentic loop back to the user prompt
                        
                except requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code == 400 and "tools" in payload:
                        # Model likely does not support tools natively. Fallback to ReAct Custom Tool Protocol.
                        payload.pop("tools")
                        
                        react_prompt = "\n\n[SYSTEM NOTICE]: Your engine does not support native tools. You MUST use tools by outputting EXACTLY this JSON block in your text:\n<tool_call>\n{\"name\": \"tool_name\", \"arguments\": {\"arg1\": \"val1\"}}\n</tool_call>\nAvailable tools: execute_command(command), write_file(filepath, content), read_file(filepath), web_search(query).\nDo not use tools if not necessary."
                        for m in payload["messages"]:
                            if m["role"] == "system" and "[SYSTEM NOTICE]" not in m["content"]:
                                m["content"] += react_prompt
                                break
                                
                        try:
                            with console.status("[bold magenta]📡 Model doesn't support native tools. Using ReAct Protocol...[/bold magenta]", spinner="dots"):
                                response = requests.post(OLLAMA_SERVER, json=payload)
                                response.raise_for_status()
                                result = response.json()
                            
                            msg = result.get("message", {})
                            content = msg.get("content", "")
                            
                            import re
                            import json
                            tool_match = re.search(r'<tool_call>(.*?)</tool_call>', content, re.DOTALL)
                            
                            if tool_match:
                                text_before = content[:tool_match.start()].strip()
                                if text_before:
                                    console.print("\n[bold red]✨ de.ci.phe.red.lab:[/bold red]")
                                    console.print(Markdown(text_before))
                                messages.append({"role": "assistant", "content": content})
                                
                                try:
                                    tool_json = json.loads(tool_match.group(1).strip())
                                    func_name = tool_json.get("name")
                                    args = tool_json.get("arguments", {})
                                    
                                    if func_name == "execute_command":
                                        tool_result = execute_command(args.get("command"))
                                    elif func_name == "write_file":
                                        tool_result = write_file(args.get("filepath"), args.get("content"))
                                    elif func_name == "read_file":
                                        tool_result = read_file(args.get("filepath"))
                                    elif func_name == "web_search":
                                        tool_result = web_search(args.get("query"))
                                    else:
                                        tool_result = f"Unknown tool: {func_name}"
                                        
                                    messages.append({
                                        "role": "user",
                                        "content": f"Tool '{func_name}' completed. Output:\n```\n{tool_result}\n```"
                                    })
                                    continue # Loop back up to let AI process result
                                except Exception as parse_err:
                                    messages.append({
                                        "role": "user",
                                        "content": f"Error parsing tool call: {parse_err}. Make sure it is valid JSON inside <tool_call>."
                                    })
                                    continue
                            else:
                                if content:
                                    console.print("\n[bold red]✨ de.ci.phe.red.lab:[/bold red]")
                                    console.print(Markdown(content))
                                    messages.append({"role": "assistant", "content": content})
                                break
                        except Exception as e2:
                            console.print(f"\n[bold red]Connection Error on retry:[/bold red] {e2}")
                            messages.pop()
                            break
                    else:
                        console.print(f"\n[bold red]Connection Error:[/bold red] {e}")
                        messages.pop() 
                        break
                except requests.exceptions.RequestException as e:
                    console.print(f"\n[bold red]Connection Error:[/bold red] {e}")
                    messages.pop() 
                    break
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[dim]Session ended.[/dim]")
            break

if __name__ == "__main__":
    main()
