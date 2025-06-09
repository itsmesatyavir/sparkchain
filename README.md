# SparkChain

A multi-account automation script for interacting with SparkChain using WebSocket, proxy support, and real-time point display in a terminal.

## 🚀 Features

- WebSocket connection with heartbeat ping
- Proxy rotation support via `aiohttp_socks`
- Random device ID generation
- Auto-token loading from file
- Real-time terminal stats (email, device ID, points)
- Minimal dependencies

## 📥 Clone the Repository

```bash
git clone https://github.com/itsmesatyavir/sparkchain.git
cd sparkchain
```

## 🛠️ Setup

### Install Dependencies

```bash
pip install aiohttp aiohttp_socks colorama
```

Or use:

```bash
pip install -r requirements.txt
```

**requirements.txt**
```
aiohttp
aiohttp_socks
colorama
```

### Add Your Tokens

```bash
nano tokens.txt
```

> Paste one token per line. Press `CTRL + O` to save and `CTRL + X` to exit.

If you want to use proxies:

```bash
nano proxy.txt
```

## 🚀 Run the Script

```bash
python main.py
```

## 📋 Libraries Used

- `aiohttp` – Async HTTP/WebSocket handling
- `aiohttp_socks` – SOCKS/HTTP proxy support
- `asyncio` – Async event loop
- `colorama` – Colored terminal output
- `datetime`, `os`, `json` – Standard Python modules

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
