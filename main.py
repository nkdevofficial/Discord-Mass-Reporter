import tls_client 
import random
import time
import json
import ctypes
import threading
import sys
import os
import platform

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from pystyle import Colors, Write, Colorate
from datetime import datetime

if not os.path.exists('input'):
    os.makedirs('input')

if not os.path.exists('dev'):
    os.makedirs('dev')

userjson = {
    "nodes": {
        "8": {
            "subkeys": {
                "Harassment": 1,
                "Spam": 2,
                "NSFW": 3,
                "Impersonation": 4,
                "Self Harm": 5
            }
        }
    }
}

serverjson = {
    "nodes": {
        "0": {
            "subkeys": {
                "Harassment": 1,
                "Spam": 2,
                "NSFW": 3,
                "Copyright": 4,
                "Illegal Content": 5
            }
        }
    }
}

with open('dev/user.json', 'w') as f:
    json.dump(userjson, f, indent=4)

with open('dev/servers.json', 'w') as f:
    json.dump(serverjson, f, indent=4)

if not os.path.exists('input/config.json'):
    defaultconfig = {
        "config": {
            "Debug": False,
            "Proxyless": False,
            "Threads": 5
        },
        "report": {
            "userid": "",
            "serverid": ""
        }
    }
    with open('input/config.json', 'w') as f:
        json.dump(defaultconfig, f, indent=4)

if not os.path.exists('input/tokens.txt'):
    with open('input/tokens.txt', 'w') as f:
        f.write("")

if not os.path.exists('input/proxies.txt'):
    with open('input/proxies.txt', 'w') as f:
        f.write("")

with open('input/config.json') as f:
    config = json.load(f)

debugmode = config['config'].get('Debug', False)

class SimpleLogger:
    def __init__(self, name="venumzmail.xyz"):
        self.name = name
    
    def _gettimestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def _formatmessage(self, level, message):
        return f"[{self.name}] [{self._gettimestamp()}] [{level}] -> {message}"
    
    def debug(self, message):
        if debugmode:
            print(Colorate.Horizontal(Colors.blue_to_purple, self._formatmessage("DEBUG", message)))
    
    def info(self, message):
        print(Colorate.Horizontal(Colors.blue_to_cyan, self._formatmessage("INFO", message)))
    
    def warning(self, message):
        print(Colorate.Horizontal(Colors.yellow_to_red, self._formatmessage("WARNING", message)))
    
    def failure(self, message):
        print(Colorate.Horizontal(Colors.red_to_black, self._formatmessage("FAILURE", message)))
    
    def success(self, message):
        print(Colorate.Horizontal(Colors.green_to_blue, self._formatmessage("SUCCESS", message)))
    
    def message(self, title, content, starttime=None, endtime=None):
        if starttime and endtime:
            elapsed = round(endtime - starttime, 3)
            print(Colorate.Horizontal(Colors.purple_to_blue, self._formatmessage(title, f"{content} In -> {elapsed} Seconds")))
        else:
            print(Colorate.Horizontal(Colors.purple_to_blue, self._formatmessage(title, content)))
    
    def question(self, prompt):
        return input(Colorate.Horizontal(Colors.blue_to_green, self._formatmessage("?", prompt)))

log = SimpleLogger()

def debug(funcormessage, *args, **kwargs) -> callable:
    if callable(funcormessage):
        @wraps(funcormessage)
        def wrapper(*args, **kwargs):
            result = funcormessage(*args, **kwargs)
            if debugmode:
                log.debug(f"{funcormessage.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if debugmode:
            log.debug(f"Debug: {funcormessage}")

def debugresponse(response) -> None:
    debug(response.headers)
    debug(response.text)
    debug(response.status_code)

class Miscellaneous:
    @debug
    def getproxies(self) -> dict:
        try:
            if config['config'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    return None
                
                proxychoice = random.choice(proxies)
                proxydict = {
                    "http": f"http://{proxychoice}",
                    "https": f"http://{proxychoice}"
                }
                return proxydict
        except FileNotFoundError:
            return None
    
    def gettokens(self) -> str:
        with open('input/tokens.txt') as f:
            tokens = [line.strip() for line in f if line.strip()]
            if not tokens:
                log.failure("No tokens found.")
                return None
            selected = random.choice(tokens)
            if ':' in selected:
                parts = selected.split(':')
                if len(parts) >= 3:
                    return parts[2]
                else:
                    return parts[-1]
            return selected
    
    @debug 
    def randomizeuseragent(self) -> str:
        discordversions = [
            "69548",
            "69547",
            "69546",
            "69545"
        ]
        
        darwinversions = [
            "24.3.0",
            "24.2.0",
            "24.1.0",
            "23.3.0"
        ]
        
        cfnetworkversions = [
            "3826.400.110",
            "3826.400.100",
            "3826.300.110"
        ]
        
        version = random.choice(discordversions)
        darwin = random.choice(darwinversions)
        cfnet = random.choice(cfnetworkversions)
        
        return f'Discord/{version} CFNetwork/{cfnet} Darwin/{darwin}'
        
    class Title:
        def __init__(self) -> None:
            self.running = False

        def starttitleupdates(self, total, starttime) -> None:
            self.running = True
            def updater():
                while self.running:
                    self.updatetitle(total, starttime)
                    time.sleep(0.5)
            threading.Thread(target=updater, daemon=True).start()

        def stoptitleupdates(self) -> None:
            self.running = False

        def updatetitle(self, total, starttime) -> None:
            try:
                elapsedtime = round(time.time() - starttime, 2)
                title = f'venumzmail.xyz | Total: {total} | Time Elapsed: {elapsedtime}s'
                
                system = platform.system()
                if system == "Windows":
                    ctypes.windll.kernel32.SetConsoleTitleW(title)
                elif system == "Darwin" or system == "Linux":
                    sys.stdout.write(f"\33]0;{title}\a")
                    sys.stdout.flush()
            except Exception as e:
                log.debug(f"Failed to update console title: {e}")

class ReportMenu:
    def __init__(self):
        with open('dev/user.json') as f:
            self.usertree = json.load(f)
        with open('dev/servers.json') as f:
            self.servertree = json.load(f)

    def displayoptions(self, nodedict):
        Write.Print("\n╔════════════[ Available Options ]════════════╗\n", Colors.red_to_blue, interval=0.000)
        for idx, (option, _) in enumerate(nodedict.items(), 1):
            Write.Print(f"     [{idx}] {option}\n", Colors.red_to_blue, interval=0.000)
        Write.Print("╚═════════════════════════════════════════════╝\n\n", Colors.red_to_blue, interval=0.000)
        return list(nodedict.values())

    def getuserbreadcrumbs(self):
        breadcrumbs = [48, 10]
        
        currentnode = self.usertree['nodes']['8']['subkeys']
        options = self.displayoptions(currentnode)
        
        choice = int(log.question("Enter your choice (number): ")) - 1
        if 0 <= choice < len(options):
            selected = options[choice]
            breadcrumbs.append(8)
            breadcrumbs.append(selected)
            
            nextnode = self.usertree['nodes'].get(str(selected))
            if isinstance(nextnode, dict) and 'subkeys' in nextnode:
                suboptions = self.displayoptions(nextnode['subkeys'])
                subchoice = int(log.question("Enter your choice (number): ")) - 1
                if 0 <= subchoice < len(suboptions):
                    breadcrumbs.append(suboptions[subchoice])
        
        return breadcrumbs

    def getserverbreadcrumbs(self):
        breadcrumbs = [0]
        
        currentnode = self.servertree['nodes']['0']['subkeys']
        options = self.displayoptions(currentnode)
        
        choice = int(log.question("Enter your choice (number): ")) - 1
        if 0 <= choice < len(options):
            selected = options[choice]
            breadcrumbs.append(selected)
            
            nextnode = self.servertree['nodes'].get(str(selected))
            if isinstance(nextnode, dict) and 'subkeys' in nextnode:
                suboptions = self.displayoptions(nextnode['subkeys'])
                subchoice = int(log.question("Enter your choice (number): ")) - 1
                if 0 <= subchoice < len(suboptions):
                    breadcrumbs.append(suboptions[subchoice])
        
        return breadcrumbs

class MassReporter:
    def __init__(self, proxydict: dict = None) -> None:
        self.session = tls_client.Session("mms_ios_3", random_tls_extension_order=True)
        self.session.headers = {
        'accept': '*/*',
        'accept-language': 'fr-HU,en-HU;q=0.9,ar-HU;q=0.8,ru-HU;q=0.7,zh-Hant-HU;q=0.6,tr-HU;q=0.5,el-HU;q=0.4,am-HU;q=0.3,hi-HU;q=0.2,es-HU;q=0.1,my-HU;q=0.1',
        'authorization': Miscellaneous().gettokens(),
        'connection': 'keep-alive',
        'content-type': 'application/json',
        'host': 'discord.com',
        'user-agent': Miscellaneous().randomizeuseragent(),
        'x-debug-options': 'bugReporterEnabled',
        'x-discord-locale': 'en-US',
        'x-discord-timezone': 'Europe/Budapest',
        }
        self.session.proxies = proxydict

    @debug
    def reportuser(self, userid: str, breadcrumbs: list) -> str | None:
        jsondata = {
            'version': '1.0',
            'variant': '2',
            'language': 'en',
            'breadcrumbs': breadcrumbs,
            'elements': {
                'user_profile_select': [
                    "photos",
                    "name",
                    "descriptors"
                ],
            },
            'user_id': userid,
            'name': 'user',
        }

        response = self.session.post('https://discord.com/api/v9/reporting/user', json=jsondata)

        debugresponse(response)

        if response.status_code == 200 and response.json().get("report_id"):
            return response.json().get("report_id")
        else:
            log.failure(f"Failed to report user {userid}, {response.text}, {response.status_code}")
        
        return None
    
    @debug
    def reportserver(self, guildid: str, breadcrumbs: list) -> str | None:
        jsondata = {
            'version': '1.0',
            'variant': '1',
            'language': 'en',
            'breadcrumbs': breadcrumbs,
            'elements': {},
            'guild_id': guildid,
            'name': 'guild'}

        response = self.session.post('https://discord.com/api/v9/reporting/guild', json=jsondata)

        debugresponse(response)

        if response.status_code == 200 and response.json().get("report_id"):
            return response.json().get("report_id")
        else:
            log.failure(f"Failed to report server {guildid}, {response.text}, {response.status_code}")
        
        return None

@debug
def report(targetid: str, reporttype: str, breadcrumbs: list, proxies: dict = None) -> tuple[bool, str]:
    try:
        Reporter = MassReporter(proxies)
        reportstart = time.time()
        
        if reporttype.lower() == "user":
            reportid = Reporter.reportuser(targetid, breadcrumbs)
        else:
            reportid = Reporter.reportserver(targetid, breadcrumbs)

        if reportid:
            log.message(
                "Discord",
                f"Successfully reported {reporttype} {targetid}. Report ID: {reportid}",
                reportstart,
                time.time()
            )
            return True
            
        return False, "Failed to get report ID"
            
    except Exception as e:
        errormsg = str(e)
        if "rate limited" in errormsg.lower():
            try:
                retryafter = e.response.json().get("retry_after", 60)
                log.warning(f"Rate limited. Waiting {retryafter} seconds...")
                time.sleep(retryafter)
            except:
                log.warning(f"Rate limited or error: {errormsg}")
        else:
            log.failure(f"Report failed: {errormsg}")
        return False, errormsg

def displaybanner():
    banner = r"""
                                                                       
                                                                       
██  ██ ██████ ███  ██ ██  ██ ██▄  ▄██ ██████ ██▄  ▄██ ▄████▄ ██ ██     
██▄▄██ ██▄▄   ██ ▀▄██ ██  ██ ██ ▀▀ ██  ▄▄▀▀  ██ ▀▀ ██ ██▄▄██ ██ ██     
 ▀██▀  ██▄▄▄▄ ██   ██ ▀████▀ ██    ██ ██████ ██    ██ ██  ██ ██ ██████ 
                                                                       
    """
    gradientbanner = Colorate.Horizontal(Colors.red_to_blue, banner)
    print(gradientbanner)

def main():
    try:
        displaybanner()
        
        Misc = Miscellaneous()
        titleupdater = Misc.Title()
        successfulreports = 0
        failedreports = 0
        starttime = time.time()

        Write.Print("""
[1] Report User
[2] Report Server

""", Colors.red_to_blue, interval=0.000)
        
        choice = log.question("Select option (1-2): ")
        
        reporttype = "user" if choice == "1" else "server" if choice == "2" else None
        
        if not reporttype:
            log.failure("Invalid choice")
            return
            
        targetid = config['report'].get(f'{reporttype}id', '')
        if not targetid:
            targetid = log.question(f"Enter {reporttype} ID to report: ")
        
        menu = ReportMenu()
        if reporttype == "user":
            breadcrumbs = menu.getuserbreadcrumbs()
        else:
            breadcrumbs = menu.getserverbreadcrumbs()
            
        reportamount = int(log.question("Enter number of reports to send: "))
        if reportamount < 1:
            log.failure("Report amount must be positive")
            return
            
        maxthreads = config['config'].get('Threads', 1)
        maxthreads = min(maxthreads, reportamount)
        
        try:
            with open('input/tokens.txt') as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    log.failure("tokens.txt is empty")
                    return
                    
            log.info(f"Loaded {len(lines)} tokens from tokens.txt")
        except FileNotFoundError:
            log.failure("tokens.txt not found in input folder")
            return
        
        titleupdater.starttitleupdates(successfulreports, starttime)
        
        with ThreadPoolExecutor(max_workers=maxthreads) as executor:
            futures = []
            for i in range(reportamount):
                proxies = Misc.getproxies()
                futures.append(
                    executor.submit(report, targetid, reporttype, breadcrumbs, proxies)
                )
                if i % 5 == 0:
                    time.sleep(0.1)
            
            for future in as_completed(futures):
                try:
                    success = future.result()
                    if success:
                        successfulreports += 1
                    else:
                        failedreports += 1
                        
                except Exception as e:
                    failedreports += 1
                    
        titleupdater.stoptitleupdates()
        
        if successfulreports > 0:
            log.success(f"Successfully sent {successfulreports}/{reportamount} reports")
        if failedreports > 0:
            log.warning(f"Failed to send {failedreports}/{reportamount} reports")
        if successfulreports == 0:
            log.failure("No reports were sent successfully")

    except KeyboardInterrupt:
        log.info("Exiting...")

    except Exception as e:
        log.failure(f"Main execution failed: {e}")
    

if __name__ == "__main__":
    main()