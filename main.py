import aiohttp
import asyncio
import json
import os
from aiohttp_socks import ProxyConnector  # pip install aiohttp_socks
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)  # Colorama init

TOKEN_FILE = "tokens.txt"
API_BASE = "https://api.sparkchain.ai"

class SparkChainClient:
    def __init__(self):
        self.proxies = []  # Agar proxy list use karna ho to yaha daal dena
        self.proxy_index = 0

    def get_next_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def print_message(self, email, proxy, color, message):
        proxy_info = f"[Proxy: {proxy}]" if proxy else ""
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{time_str}] {email} {proxy_info} - {message}{Style.RESET_ALL}")

    async def user_profile(self, email, token, proxy=None):
        url = f"{API_BASE}/profile"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://sparkchain.ai"
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None

        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Sample expected structure:
                        # {
                        #   "email": "...",
                        #   "name": "...",
                        #   "total_points": 12345,
                        #   "points_breakdown": {
                        #        "network_points": 90,
                        #        "referral_points": 0,
                        #        ...
                        #   }
                        # }
                        return data
                    else:
                        self.print_message(email, proxy, Fore.RED, f"Profile fetch failed, status: {resp.status}")
        except Exception as e:
            self.print_message(email, proxy, Fore.RED, f"Exception in profile fetch: {e}")
        return None

    async def connect_websocket(self, email: str, token: str, device_id: str, proxy=None):
        wss_url = f"wss://ws-v2.sparkchain.ai/socket.io/?token={token}&device_id={device_id}&device_version=0.9.2&EIO=4&transport=websocket"
        headers = {
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Host": "ws-v2.sparkchain.ai",
            "Origin": "chrome-extension://jlpniknnodfkbmbgkjelcailjljlecch",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-WebSocket-Key": "112eUtlasNicqwoPnggJYw==",
            "Sec-WebSocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }

        while True:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=120))
            try:
                async with session.ws_connect(wss_url, headers=headers) as wss:

                    async def send_up(sid):
                        message_3 = f'42{json.dumps(["up",{"id":sid}])}'
                        while True:
                            await asyncio.sleep(120)
                            await wss.send_str(message_3)
                            self.print_message(email, proxy, Fore.WHITE,
                                f"Device ID {device_id} - Sent Message: {message_3}"
                            )

                    self.print_message(email, proxy, Fore.GREEN, f"Websocket Connected for Device ID {device_id}")
                    registered = False
                    send_up_task = None

                    while True:
                        try:
                            response = await wss.receive_str()
                            if response and not registered:
                                self.print_message(email, proxy, Fore.CYAN, f"Received Message: {response}")
                                await wss.send_str('40')
                                self.print_message(email, proxy, Fore.GREEN, "Sent Message: 40")
                                registered = True

                            elif response and registered:
                                if response == "2":
                                    await wss.send_str('3')
                                    self.print_message(email, proxy, Fore.BLUE, "Node Connection Established")
                                else:
                                    if send_up_task is None:
                                        result = json.loads(response[2:])
                                        sid = result["sid"]
                                        send_up_task = asyncio.create_task(send_up(sid))
                                        self.print_message(email, proxy, Fore.CYAN, f"Received Message: {response}")
                        except Exception as e:
                            self.print_message(email, proxy, Fore.RED, f"WebSocket connection closed: {e}")
                            if send_up_task:
                                send_up_task.cancel()
                                try:
                                    await send_up_task
                                except asyncio.CancelledError:
                                    self.print_message(email, proxy, Fore.YELLOW, "Send UP Message Cancelled")
                            await asyncio.sleep(5)
                            break
            except Exception as e:
                self.print_message(email, proxy, Fore.RED, f"WebSocket Not Connected: {e}")
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                self.print_message(email, proxy, Fore.YELLOW, "WebSocket Closed")
                break
            finally:
                await session.close()

    async def process_get_user_earning(self, email: str, token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            user = await self.user_profile(email, token, proxy)
            if user:
                total_points = user.get("total_points", 0)
                points_breakdown = user.get("points_breakdown", {})
                self.print_message(email, proxy, Fore.WHITE, f"--- Forest Army - SparkChain Stats ---")
                self.print_message(email, proxy, Fore.WHITE, f"Name   : {user.get('name', 'N/A')}")
                self.print_message(email, proxy, Fore.WHITE, f"Email  : {user.get('email', 'N/A')}")
                self.print_message(email, proxy, Fore.WHITE, "")
                self.print_message(email, proxy, Fore.WHITE, f"Total Points         : {total_points} PTS")
                # Show all breakdown points if available, else show 0
                keys_map = {
                    "network_points": "Network Points",
                    "referral_points": "Referral Points",
                    "referral_bonus_points": "Referral Bonus Points",
                    "complete_task_points": "Complete Task Points",
                    "claim_points": "Claim Points",
                    "reply_points": "Reply Points",
                    "upgrade_points": "Upgrade Points"
                }
                for k, label in keys_map.items():
                    val = points_breakdown.get(k, 0)
                    self.print_message(email, proxy, Fore.WHITE, f"{label:<22}: {val} PTS")
                self.print_message(email, proxy, Fore.WHITE, "")
                calculated_total = sum(points_breakdown.get(k, 0) for k in keys_map.keys())
                self.print_message(email, proxy, Fore.WHITE, f"Calculated Total Points: {calculated_total} PTS")
                self.print_message(email, proxy, Fore.WHITE, "-"*40)
            else:
                self.print_message(email, proxy, Fore.RED, "Failed to fetch user earnings")
            await asyncio.sleep(10 * 60)  # 10 minutes

def read_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: Token file '{TOKEN_FILE}' not found. Please create it with your Bearer token.")
        exit(1)
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
    if not token:
        print(f"Error: Token file '{TOKEN_FILE}' is empty.")
        exit(1)
    return token

async def main():
    client = SparkChainClient()
    token = read_token()
    email = "forestarmy - SPARKCHAIN"  # Apna email yaha daal
    device_id = "a3f9b7c4-e8d1-4f02-9c5a-27d89e06fcb7"  # Apna device id yaha daal
    use_proxy = False  # Agar proxy use karna hai to True kar

    # Ek bar subscribe to karo meri jan
    await asyncio.gather(
        client.connect_websocket(email, token, device_id, proxy=None),
        client.process_get_user_earning(email, token, use_proxy)
    )

if __name__ == "__main__":
    asyncio.run(main())
