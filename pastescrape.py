#!/usr/bin/python3
import requests, time, random
from bs4 import BeautifulSoup
from pathlib import Path
from os import path
from sys import exit

raw_paste_url = "https://www.pastebin.com/raw"
request_url = "https://www.pastebin.com/archive"

#file paths that will be used
file_path = Path(__file__).resolve().parent
log_path = file_path / Path("saves/log.txt")
agents_path = file_path / Path("agents.txt")
keywords_path = file_path / Path("keywords.txt")
parsed_path = file_path / Path("parsed.txt")
saves = file_path / Path("saves")

#im so lazy :)
if saves.exists() == False:
	saves.mkdir()
log_path.touch(exist_ok=True)
agents_path.touch(exist_ok=True)
keywords_path.touch(exist_ok=True)
parsed_path.touch(exist_ok=True)

def write(path, mode, text):
	with open(path, mode) as file:
		file.write(text)

#split keywords file into a list, close if it's empty.
with open(keywords_path, "r+") as f:
	keywords = [keyword.strip("\n") for keyword in f.readlines()]
	if keywords == []:
		write(log_path, "a+", time.strftime("[%Y-%m-%d] Keywords file empty, closing.\n"))
		exit()

with open(agents_path, "r+") as f:
	request_agents = [agent.strip("\n") for agent in f.readlines()]
	#Using random user-agents to keep our ip from being blocked
	#This wouldn't be a problem if I were allowed to use the
	#scraping API, but that's limited to Pro users. And I
	#would become a pro user, but they're "sold out"?

#get a list of the pastes we've already read
with open(parsed_path, "r+") as f:
	parsed_pastes = [paste.strip("\n") for paste in f.readlines()]

#check to make sure there is internet
try:
	requests.head("https://www.google.com", timeout=5)
except requests.ConnectionError:
	write(log_path, "a+", time.strftime("[%Y-%m-%d] No internet connection, closing.\n"))
	exit()

#request the recent public pastes, and parse the html
request = requests.get(request_url, headers={"User-Agent": random.choice(request_agents)})
soup = BeautifulSoup(request.text, "html.parser")
table = soup.find("div", class_="archive-table")

write(log_path, "a+", time.strftime("[%Y-%m-%d] Starting scrape.\n"))
for link in table.find_all("a"):
	paste = link.get("href")

	if paste.startswith("/archive"): continue
	if paste in parsed_pastes: continue

	write(parsed_path, "a+", paste + "\n")
	write(log_path, "a+", time.strftime("[%Y-%m-%d] Reading " + paste + ".\n"))

	current_paste = requests.get(raw_paste_url + paste,
			headers={"User-Agent": random.choice(request_agents)})

	#for every keyword in our list, check if it's in the current paste.
	#if it is, save the paste and move to the next paste in the loop.
	for keyword in keywords:
		if keyword.lower() in current_paste.text.lower():
			write(log_path, "a+", "[{0}] Keyword < {1} > found in {2}!\n".format(
						time.strftime("%Y-%m-%d"), keyword, paste))

			dated_path = saves / time.strftime("%Y-%m-%d")
			if dated_path.exists() == False:
				dated_path.mkdir()
				write(log_path, "a+", "[{0}] Making {1}...\n".format(
							time.strftime("%Y-%m-%d"), dated_path))

			with open(dated_path / Path(paste[1:] + ".txt"), "w+") as f:
				f.write("[*] KEYWORD < {0} >\n".format(keyword))
				f.write("-"*20 + "\n")
				f.write(current_paste.text)
			break
