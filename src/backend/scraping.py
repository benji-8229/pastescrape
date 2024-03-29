import requests, re
from random import choice
from bs4 import BeautifulSoup
from helpers import Helpers

class Scraping:
    U_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
                ]
    BASE_DOM = "https://pastebin.com"
    SCRAPE_URL = "https://pastebin.com/archive"
    
    @staticmethod
    def get_header():
        return {"User-Agent": choice(Scraping.U_AGENTS)}
    
    @staticmethod
    def is_valid_id(id, check_404=True):
        id = id.strip("/").strip()
        
        if len(id) != 8:
            return False
        elif not id.isalnum():
            return False
        
        if check_404:
            content = requests.get(f"{Scraping.BASE_DOM}/{id}", headers=Scraping.get_header())
            soup = BeautifulSoup(content.text, features="html.parser")
            title = soup.find("div", class_="content__title")
            
            return title != None and title.contents[0] != "Not Found (#404)"
        else:
            return True
            
    @staticmethod
    def scrape_paste_content(id):
        id = id.strip("/").strip()

        data = {"text": "", "title": "Untitled", "language": "", "time": "", "user": "Guest", "tags": "", "id": id}
        
        if not Scraping.is_valid_id(id):
            return data
        
        # it is painful to extract the text from the pastebin page, so we request the raw page aswell
        raw_content = requests.get(f"{Scraping.BASE_DOM}/raw/{id}", headers=Scraping.get_header())
        main_content = requests.get(f"{Scraping.BASE_DOM}/{id}", headers=Scraping.get_header())
        raw_content.encoding = "utf-8"
        main_content.encoding = "utf-8"
        
        soup = BeautifulSoup(main_content.text, features="html.parser")
        
        data["text"] = raw_content.text
        data["title"] = soup.find("h1").contents[0]
        data["language"] = soup.find_all("a", href=True, class_="btn -small h_800")[0].contents[0]
        data["time"] = Helpers.convert_pastebin_date(soup.find("div", class_="date").find("span").get("title"))
        
        # walrus operator :OO O O OO 
        if user := soup.find("div", class_="username").find("a"):
            data["user"] = user.contents[0]
        if tags := soup.find("div", class_="tags"):
            data["tags"] = " ".join([x.contents[0] for x in tags.find_all("a")])
            
        return data
    
    @staticmethod
    def scrape_ids():
        # In a perfect world we would integrate with the PasteBin premium API for our scraping, but they haven't sold those accounts in years.
        content = requests.get(Scraping.SCRAPE_URL, headers=Scraping.get_header())
        
        # implement connection tests and retry logic here
        match content.status_code:
            case _:
                pass
                
        soup = BeautifulSoup(content.text, features="html.parser")
        
        # for every link in the soup, add the link to ids if the link matches the re pattern
        id_list = [x["href"].strip("/") for x in soup.find_all("a", href=True) if re.match(r"^/([A-Za-z0-9_.]{8})$", x["href"])]

        return set(id_list)
    
    