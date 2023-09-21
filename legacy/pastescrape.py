#!/usr/bin/python3
import requests
import time
import random
import json
import logging
from bs4 import BeautifulSoup
from pathlib import Path
from sys import exit, stdout


def write(path, mode, text):
    with open(path, mode) as file:
        file.write(text)


# set up config and file paths
file_path = Path(__file__).parent
conf_path = file_path / Path("config.conf")
conf_path.touch(exist_ok=True)
try:
    conf_data = json.load(conf_path.open("r"))
except ValueError:
    # conf file empty, add fields and close
    print("[*] Config file empty, generating empty fields.")
    json.dump(
        {"saves_path": "", "logs_path": "", "user_agents": [], "keywords": []},
        conf_path.open("w+"),
    )
    exit()

# read paths from config and make sure they're valid
if conf_data["saves_path"] == "" or conf_data["logs_path"] == "":
    print("[*] Saves or logs path empty, check config.")
    exit(1)
else:
    saves = Path(conf_data["saves_path"])
    log_path = Path(conf_data["logs_path"])
    parsed_path = saves / Path(".parsed.txt")
    if not saves.exists() or saves.is_file():
        print(f"[*] Directory {saves} does not exist or points to a file, closing.")
        exit(1)
    elif not log_path.parent.exists():
        print(f"[*] Log directory {log_path.parent} does not exist, closing.")
        exit(1)
    elif not log_path.is_file():
        print(f"[*] Log path {log_path} does not point to a file, closing.")
        exit(1)

raw_paste_url = "https://www.pastebin.com/raw"
request_url = "https://www.pastebin.com/archive"

# logging setup
logging.basicConfig(
    format="%(asctime)s %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler(log_path, mode="a+"), logging.StreamHandler(stdout)],
)
logging.info("pastescrape.py opened.")

keywords = conf_data["keywords"]
if keywords == []:
    logging.critical("Keywords empty, closing.")
    exit(1)

# I understand it doesn't look great to be using random user agents
# to avoid being blocked. I would much rather use PasteBin's scraping
# API, but that's for pro accounts. And they are "sold out" of those???
request_agents = conf_data["user_agents"]
if request_agents == []:
    logging.warning("User-Agents empty, higher chance of being blocked.")
    request_agents.append("")

# get a set of the pastes we've already read
# use a set because the contains check is O(1) instead of O(n)
with open(parsed_path, "r+") as f:
    parsed_pastes = set([paste.strip("\n") for paste in f.readlines()])

# request the recent public pastes, and parse the html
try:
    request = requests.get(
        request_url, headers={"User-Agent": random.choice(request_agents)}
    )
except requests.ConnectionError:
    logging.critical("No internet connection, closing.")
    exit(1)

request.encoding = "utf-8"
soup = BeautifulSoup(request.text, "html.parser")
table = soup.find("div", class_="archive-table")

logging.info("Starting to scrape links.")
for link in table.find_all("a"):
    paste = link.get("href")

    if paste.startswith("/archive"):
        continue
    if paste in parsed_pastes:
        continue

    write(parsed_path, "a+", f"{paste}\n")
    current_paste = requests.get(
        raw_paste_url + paste, headers={"User-Agent": random.choice(request_agents)}
    )

    logging.info("Checking paste {0} for keywords.".format(paste))

    # for every keyword in our list, check if it's in the current paste.
    # if it is, save the paste and move to the next paste in the loop.
    for keyword in keywords:
        if keyword.lower() in current_paste.text.lower():
            logging.info(f"Keyword < {keyword} > found in paste {paste}.")
            dated_path = saves / time.strftime("%Y-%m-%d")
            if dated_path.exists() == False:
                dated_path.mkdir()
                logging.info(f"Creaing directory {dated_path}.")
            with open(
                dated_path / Path(f"{keyword}_{paste[1:]}.txt"), "w+", encoding="utf8"
            ) as f:
                f.write(f"[*] KEYWORD < {keyword} >\n")
                f.write(("-" * 20 + "\n"))
                f.write(current_paste.text)
            break

logging.info("pastescrape.py finished running.\n")
