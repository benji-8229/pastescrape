# pastescrape
`pastescrape` is a simple script to regularly read recent, public pastes on pastebin and save anything interesting.

### Installation and Setup
1. run `gh repo clone pastescrape`
2. run `sudo python pastescrape.py` to generate directories and files
3. configure `agents.txt` and `keywords.txt`.

      these are both newline seperated lists. agents.txt contains user-agents that will randomly be used to keep our ip from being blocked. keywords.txt determines
      what pastes are considered interesting. keywords are **not** case sensitive.
4. schedule it to run automatically in ***sudo's*** crontab. 

      running it every 3-4 hours should be plenty, and the longer you wait the less likely you are to get blocked.
5. (optional) cd to the `saved` directory and run `sudo python -m http.server 80`. this allows you to type your devices ip anywhere on your network and see the saved pastes.

### Todo
merge user-agents and keywords into a single config file
