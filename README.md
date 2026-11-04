# cryptos CLI

This is a lightweight command-line interface for our lab to connect to the central workstation AI. You do not need to install heavy models on your local machine; this tool streams responses directly from the workstation.

## Prerequisites
- Python 3 installed on your machine.
- You must be connected to the lab network.

## Installation (Mac & Linux)

To make it a globally accessible command (`cryptos`), open your terminal and run:

```bash
# Make it executable
chmod +x lab-cli.py

# Move it to your local binaries so you can run it from anywhere
sudo mv lab-cli.py /usr/local/bin/cryptos
```

## Usage

Simply open your terminal and type:
```bash
cryptos
```

To exit the chat, type `exit` or `quit`.

## Server Administration (Admin Only)
For the lab members to be able to install the CLI or receive Over-The-Air (OTA) updates, the central host server must be running the distribution web server.

To start the web server, run this command on the admin machine and keep the terminal open:
```bash
python3 -m http.server 9000 --directory /home/crypto_nn/lab-ai-cli
```
