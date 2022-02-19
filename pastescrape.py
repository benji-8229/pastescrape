#!/usr/bin/python3
import requests, time, random
from bs4 import BeautifulSoup
from pathlib import Path
from os import path
from sys import exit

raw_paste_url = "https://www.pastebin.com/raw"
request_url = "https://www.pastebin.com/archive"

file_path = Path(__file__).resolve().parent
txt_path = file_path / Path("txt")
agents_path = file_path / Path("txt/agents.txt")
keywords_path = file_path / Path("txt/keywords.txt")
parsed_pastes_path = file_path / Path("txt/parsed_pastes.txt")
saved_pastes_path = file_path / Path("saved_pastes")

#Create any dir / files if needed
if txt_path.exists() == False:
	print("[*] Creating txt/...")
	txt_path.mkdir()
if keywords_path.exists() == False:
	print("[*] Creating txt/keywords.txt...")
	with open(keywords_path, "w") as f: pass
if agents_path.exists() == False:
	print("[*] Creating txt/agents.txt...")
	with open(agents_path, "w") as f: pass
if parsed_pastes_path.exists() == False:
	print("[*] Creating txt/parsed_pastes.txt...")
	with open(parsed_pastes_path, "w") as f: pass
if saved_pastes_path.exists() == False:
	print("[*] Creating saved_pastes/...")
	saved_pastes_path.mkdir()

with open(keywords_path, "r") as f:
	keywords = [keyword.strip("\n") for keyword in f.readlines()]
	if keywords == []:
		print("[!] KEYWORD FILE EMPTY! Closing program.")
	exit()

with open(agents_path, "r") as f:
	request_agents = [agent.strip("\n") for agent in f.readlines()]
	#Using random user-agents to avoid our ip being blocked
	#This wouldn't be a problem if I were allowed to use the
	#scraping API, but that's limited to Pro users. And I
	#would become a pro user, but they're "sold out"?

with open(parsed_pastes_path, "r") as f:
	parsed_pastes = [paste.strip("\n") for paste in f.readlines()]

try:
	requests.head("https://www.google.com", timeout=5)
except requests.ConnectionError:
	print("[!] No internet connection, closing.")
	exit()

request = requests.get(request_url,
			headers={"User-Agent": random.choice(request_agents)})

soup = BeautifulSoup(request.text, "html.parser")
table = soup.find("div", class_="archive-table")
links = []

for link in table.find_all("a"):
	paste = link.get("href")

	if paste.startswith("/archive"): continue
	if paste in parsed_pastes: continue
	#Discard worthless links and pastes that are in parsed_pastes

	with open(parsed_pastes_path, "r+") as f:
		f.write(paste + "\n")
	#Add new pastes to parsed_pastes

	print("[*] Reading {0}...".format(paste))
	current_paste = requests.get(raw_paste_url + paste,
			headers={"User-Agent": random.choice(request_agents)})

	for keyword in keywords:
		if keyword.lower() in current_paste.text.lower():
			print("[*] Found >{0}< in paste {1}! Saving...".format(
			keyword, paste))

			dated_path = saved_pastes_path / time.strftime("%Y-%m-%d")
			if dated_path.exists() == False:
				dated_path.mkdir()
				print("[*] Making {0}...".format(dated_path))

			with open(dated_path / Path(paste[1:] + ".txt"), "a+") as f:
				f.write(current_paste.text)
			break
