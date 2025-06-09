
from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, base64, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Sparkchain:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://sparkchain.ai",
            "Priority": "u=1, i",
            "Referer": "https://sparkchain.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping Script {Fore.GREEN + Style.BRIGHT}Sparkchain AI - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT} Subscribe {Fore.YELLOW + Style.BRIGHT}https://t.me/forestarmy 
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, email):
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            email = parsed_payload["email"]
            
            return email
        except Exception as e:
            return None
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_message(self, email, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                proxy_choice = int(input("Choose [1/2/3] -> ").strip())

                if proxy_choice in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if proxy_choice == 1 else 
                        "Run With Private Proxy" if proxy_choice == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        nodes_count = 0
        if proxy_choice in [1, 2]:
            while True:
                try:
                    nodes_count = int(input("How Many Nodes Do You Want to Run For Each Account? -> ").strip())
                    if nodes_count > 0:
                        break
                    else:
                        print(f"{Fore.RED+Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        return nodes_count, proxy_choice
    
    async def user_profile(self, email: str, token: str, proxy=None, retries=5):
        url = "https://api.sparkchain.ai/profile"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def task_lists(self, email: str, token: str, proxy=None, retries=5):
        url = "https://api.sparkchain.ai/tasks"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET Available Tasks Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def complete_tasks(self, email: str, token: str, task_id: int, title: str, proxy=None, retries=5):
        url = "https://api.sparkchain.ai/tasks"
        data = json.dumps({"id":task_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 500:
                            return self.print_message(self.mask_account(email), proxy, Fore.WHITE, 
                                f"Task {title}"
                                f"{Fore.RED + Style.BRIGHT} Isn't Completed: {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}Not Eligible{Style.RESET_ALL}"
                            )
                        
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"Task {title} Isn't Completed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def user_device(self, email: str, token: str, proxy=None, retries=5):
        url = "https://api.sparkchain.ai/devices"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(email, proxy, Fore.RED, f"GET Device ID Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
        
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
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=120))
            try:
                async with session.ws_connect(wss_url, headers=headers) as wss:

                    async def send_up(sid):
                        message_3 = f'42{json.dumps(["up",{"id":sid}])}'
                        while True:
                            await asyncio.sleep(120)
                            await wss.send_str(message_3)
                            self.print_message(email, proxy, Fore.WHITE, 
                                f"Device ID {device_id} "
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Sent Message: {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}{message_3}{Style.RESET_ALL}"
                            )

                    self.print_message(email, proxy, Fore.WHITE, 
                        f"Device ID {device_id}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                    )
                    registered = False
                    send_up_message = None

                    while True:
                        try:
                            response = await wss.receive_str()
                            if response and not registered:
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Device ID {device_id} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Received Message: {Style.RESET_ALL}"
                                    f"{Fore.BLUE + Style.BRIGHT}{response}{Style.RESET_ALL}"
                                )
                                message_1 = '40'
                                await wss.send_str(message_1)
                                self.print_message(email, proxy, Fore.WHITE, 
                                    f"Device ID {device_id} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Sent Message: {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}{message_1}{Style.RESET_ALL}"
                                )
                                registered = True

                            elif response and registered:
                                if response == "2":
                                    message_2 = '3'
                                    await wss.send_str(message_2)
                                    print(
                                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT}Node Connection Estabilished{Style.RESET_ALL}",
                                        end="\r",
                                        flush=True
                                    )

                                else:
                                    if send_up_message is None:
                                        result = json.loads(response[2:])
                                        sid = result["sid"]
                                        send_up_message = asyncio.create_task(send_up(sid))

                                        self.print_message(email, proxy, Fore.WHITE, 
                                            f"Device ID {device_id} "
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Received Message: {Style.RESET_ALL}"
                                            f"{Fore.BLUE + Style.BRIGHT}{response}{Style.RESET_ALL}"
                                        )
                                
                        except Exception as e:
                            self.print_message(email, proxy, Fore.WHITE, 
                                f"Device ID {device_id} "
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} Websocket Connection Closed: {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                            )
                            if send_up_message:
                                send_up_message.cancel()
                                try:
                                    await send_up_message
                                except asyncio.CancelledError:
                                    self.print_message(email, proxy, Fore.WHITE, 
                                        f"Device ID {device_id}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Sent UP Message Cancelled{Style.RESET_ALL}"
                                    )
                                    
                            await asyncio.sleep(5)
                            break

            except Exception as e:
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Device ID {device_id} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Websocket Not Connected: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.print_message(email, proxy, Fore.WHITE, 
                    f"Device ID {device_id}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()
            
    async def process_get_user_earning(self, email: str, token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            balance = "N/A"

            user = await self.user_profile(email, token, proxy)
            if user:
                balance = user.get("total_points", 0)
                self.print_message(email, proxy, Fore.WHITE, f"Earning Total: {balance} PTS")
                
            await asyncio.sleep(10 * 60)

    async def process_complete_tasks(self, email: str, token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            tasks = await self.task_lists(email, token, proxy)
            if tasks:
                completed = False
                for task in tasks:
                    if task:
                        task_id = task.get("id")
                        title = task.get("name")
                        amount = task.get("reward_amount")
                        type = task.get("reward_type")

                        completed_at = task.get("completed_at")
                        if completed_at is None:
                            complete = await self.complete_tasks(email, token, task_id, title, proxy)
                            if complete:
                                self.print_message(self.mask_account(email), proxy, Fore.WHITE, 
                                    f"Task {title}"
                                    f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{amount} {type}{Style.RESET_ALL}"
                                )
                    else:
                        completed = True

                if completed:
                    self.print_message(self.mask_account(email), proxy, Fore.GREEN, 
                        f"All Available Tasks Is Completed"
                    )
                
            await asyncio.sleep(24 * 60 * 60)
            
    async def process_get_device_id(self, email: str, token: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        devices = None
        while devices is None:
            devices = await self.user_device(email, token, proxy)
            if not devices:
                proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                await asyncio.sleep(5)
                continue

            device_id = devices[0].get("device_id")
            
            self.print_message(email, proxy, Fore.GREEN, "GET Device ID Success")
            return device_id
        
    async def process_accounts(self, email: str, token: str, nodes_count: int, use_proxy: bool):
        tasks = []
        tasks.append(asyncio.create_task(self.process_get_user_earning(email, token, use_proxy)))
        tasks.append(asyncio.create_task(self.process_complete_tasks(email, token, use_proxy)))

        device_id = await self.process_get_device_id(email, token, use_proxy)
        if device_id:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            if use_proxy:
                for i in range(nodes_count):
                    tasks.append(asyncio.create_task(self.connect_websocket(email, token, device_id, proxy)))
                    proxy = self.rotate_proxy_for_account(email)
            else:
                tasks.append(asyncio.create_task(self.connect_websocket(email, token, device_id, proxy)))

        await asyncio.gather(*tasks)
        
    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]
            
            nodes_count, use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for token in tokens:
                    if token:
                        email = self.decode_token(token)
                        tasks.append(asyncio.create_task(self.process_accounts(email, token, nodes_count, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Sparkchain()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Sparkchain AI - BOT{Style.RESET_ALL}                                       "                              
        )
