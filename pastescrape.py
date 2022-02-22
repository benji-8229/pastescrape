#!/usr/bin/python3
import requests, time, random, json, logging
from bs4 import BeautifulSoup
from pathlib import Path
from sys import exit

raw_paste_url = "https://www.pastebin.com/raw"
request_url = "https://www.pastebin.com/archive"

#file paths that will be used
file_path = Path.cwd()
log_path = file_path / Path("saves/log.txt")
conf_path = file_path / Path("config.conf")
parsed_path = file_path / Path("saves/.parsed.txt")
saves = file_path / Path("saves")

#im so lazy :)
if saves.exists() == False:
	saves.mkdir()
log_path.touch(exist_ok=True)
conf_path.touch(exist_ok=True)
parsed_path.touch(exist_ok=True)

def write(path, mode, text):
	with open(path, mode) as file:
		file.write(text)

#logging setup
logging.basicConfig(filename=log_path, format="%(asctime)s %(levelname)s - %(message)s", level=logging.INFO, filemode="a")
logging.info("pastescrape.py opened.")

try:
	conf_data = json.load(conf_path.open("r"))
except ValueError:
	#conf file empty, add fields and close
	json.dump({"user_agents": [], "keywords": []}, conf_path.open("w+"))
	logging.info("Creating config file.")

keywords = conf_data["keywords"]
if keywords == []:
	logging.critical("Keywords empty, closing.")
	exit()

#I understand it doesn't look great to be using random user agents
#to avoid being blocked. I would much rather use PasteBin's scraping
#API, but that's for pro accounts. And they are "sold out" of those???
request_agents = conf_data["user_agents"]
if request_agents == []:
	logging.warning("User-Agents empty, higher chance of being blocked.")

#get a set of the pastes we've already read
#use a set because the contains check is O(1) instead of O(n)
with open(parsed_path, "r+") as f:
	parsed_pastes = set([paste.strip("\n") for paste in f.readlines()])

#check to make sure there is internet
try:
	requests.head("https://www.google.com", timeout=5)
except requests.ConnectionError:
	logging.critical("No internetion connection, closing.")
	exit()

#request the recent public pastes, and parse the html
request = requests.get(request_url, headers={"User-Agent": random.choice(request_agents)})
soup = BeautifulSoup(request.text, "html.parser")
table = soup.find("div", class_="archive-table")

logging.info("Starting to scrape links.")
for link in table.find_all("a"):
	paste = link.get("href")

	if paste.startswith("/archive"): continue
	if paste in parsed_pastes: continue

	write(parsed_path, "a+", f"{paste}\n")
	current_paste = requests.get(raw_paste_url + paste, headers={"User-Agent": random.choice(request_agents)})

	logging.info("Checking paste {0} for keywords.".format(paste))

	#for every keyword in our list, check if it's in the current paste.
	#if it is, save the paste and move to the next paste in the loop.
	for keyword in keywords:
		if keyword.lower() in current_paste.text.lower():
			logging.info(f"Keyword < {keyword} > found in paste {paste}.")
			dated_path = saves / time.strftime("%Y-%m-%d")
			if dated_path.exists() == False:
				dated_path.mkdir()
				logging.info(f"Creaing directory {dated_path}.")
			with open(dated_path / Path(f"{keyword}_{paste[1:]}.txt"), "w+") as f:
				f.write(f"[*] KEYWORD < {keyword} >\n")
				f.write("-"*20 + "\n")
				f.write(current_paste.text)
			break

logging.info("pastescrape.py finished running.\n")
