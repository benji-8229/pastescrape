#!/usr/bin/python3
import requests, time, random, json
from bs4 import BeautifulSoup
from pathlib import Path
from sys import exit

raw_paste_url = "https://www.pastebin.com/raw"
request_url = "https://www.pastebin.com/archive"

#file paths that will be used
file_path = Path(__file__).resolve().parent
log_path = file_path / Path("saves/log.txt")
conf_path = file_path / Path("config.conf")
parsed_path = file_path / Path(".parsed.txt")
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

#organize logs a bit
write(log_path, "a+", "-" * 30 + "\n")
write(log_path, "a+", time.strftime("\n[%D] Running pastescrape.py...\n"))

try:
	conf_data = json.load(conf_path.open("r"))
except ValueError:
	#conf file empty, add fields and close
	json.dump({"user_agents": [], "keywords": []}, conf_path.open("w+"))
	write(log_path, "a+", time.strftime("[%T] Config file empty, closing...\n"))
	exit()

keywords = conf_data["keywords"]
if keywords == []:
	write(log_path, "a+", time.strftime("[%T] Keywords file empty, closing.\n"))
	exit()

#I understand it doesn't look great to be using random user agents
#to avoid being blocked. I would much rather use PasteBin's scraping
#API, but that's for pro accounts. And they are "sold out" of those???
request_agents = conf_data["user_agents"]

#get a set of the pastes we've already read
#use a set because the contains check is O(1) instead of O(n)
with open(parsed_path, "r+") as f:
	parsed_pastes = set([paste.strip("\n") for paste in f.readlines()])

#check to make sure there is internet
try:
	requests.head("https://www.google.com", timeout=5)
except requests.ConnectionError:
	write(log_path, "a+", time.strftime("[%T] No internet connection, closing.\n"))
	exit()

#request the recent public pastes, and parse the html
request = requests.get(request_url, headers={"User-Agent": random.choice(request_agents)})
soup = BeautifulSoup(request.text, "html.parser")
table = soup.find("div", class_="archive-table")

write(log_path, "a+", time.strftime("[%T] Starting scrape.\n"))
for link in table.find_all("a"):
	paste = link.get("href")

	if paste.startswith("/archive"): continue
	if paste in parsed_pastes: continue

	write(parsed_path, "a+", paste + "\n")
	write(log_path, "a+", time.strftime("[%T] Reading " + paste + ".\n"))

	current_paste = requests.get(raw_paste_url + paste,
			headers={"User-Agent": random.choice(request_agents)})

	#for every keyword in our list, check if it's in the current paste.
	#if it is, save the paste and move to the next paste in the loop.
	for keyword in keywords:
		if keyword.lower() in current_paste.text.lower():
			write(log_path, "a+", "[{0}] Keyword < {1} > found in {2}!\n".format(
						time.strftime("%T"), keyword, paste))

			dated_path = saves / time.strftime("%Y-%m-%d")
			if dated_path.exists() == False:
				dated_path.mkdir()
				write(log_path, "a+", "[{0}] Making {1}...\n".format(
							time.strftime("%T"), dated_path))

			with open(dated_path / Path(paste[1:] + ".txt"), "w+") as f:
				f.write("[*] KEYWORD < {0} >\n".format(keyword))
				f.write("-"*20 + "\n")
				f.write(current_paste.text)
			break

write(log_path, "a+","\n" + "-" * 30 + "\n")
