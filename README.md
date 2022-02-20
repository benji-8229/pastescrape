# pastescrape
`pastescrape` is a simple script to regularly read recent, public pastes on pastebin and save anything interesting.

### Why?
Simple curiosity. Lots of interesting things get posted to PasteBin, from drug dealer's menus to malware. I am interested in documenting and recording the interesting things that would otherwise go unnoticed.

### Installation and Setup
1. Run `gh repo clone pastescrape`.

2. Run `sudo python pastescrape.py` to generate directories and files.

3. Configure `agents.txt` and `keywords.txt`. These are both newline seperated lists. Agents.txt contains user-agents that will randomly be used to keep our ip from being blocked. Keywords.txt determines what pastes are considered interesting. Keywords are **not** case sensitive.

4. Schedule it to run automatically in ***sudo's*** crontab. Running it every 5-6 hours should be plenty, and the longer you wait the less likely you are to get blocked.

5. (Optional) cd to the `saved` directory and run `sudo python -m http.server 80`. This allows you to type your devices ip anywhere on your network and see the saved pastes.

### Todo
merge user-agents and keywords into a single config file
