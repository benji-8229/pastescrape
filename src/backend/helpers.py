import json, re
from pathlib import Path


class Helpers:
    CONFIG_PATH = Path(__file__).resolve().parent / Path("jnk") / Path("config.cfg")
    CACHE_PATH = Path(__file__).resolve().parent / Path("jnk") / Path("CACHE.cache")
    CONFIG_STRUCT = {"logging": "verbose/vital",
                     "log_path": "log.txt",
                     "refresh_interval": 60 * 5,
                     "db_uri": "",
                     "db_name": "",
                     "db_collection_name": ""
                     }
    MONTH_MAP = {"January": 1,
                "February": 2,
                "March": 3,
                "April": 4,
                "May": 5,
                "June": 6,
                "July": 7,
                "August": 8,
                "September": 9,
                "October": 10,
                "November": 11,
                "December": 12
                }
    
    @staticmethod 
    def convert_pastebin_date(strv):
        matches = re.findall("\S+", strv)
        matches.remove("of")
        
        month = Helpers.MONTH_MAP[matches[2]]
        day = re.match(r'([0-9]+)', matches[1]).groups()[0]
        year = matches[3]
        stamp = " ".join(matches[4:7])
        
        return f"{month}/{day}/{year} {stamp}"

    @staticmethod
    def config_get():
        if not Path.exists(Helpers.CONFIG_PATH):
            with open(Helpers.CONFIG_PATH, "w") as config_file:
                config_file.write(json.dumps(Helpers.CONFIG_STRUCT, indent=4))
            raise Exception("Unconfigured config file.")

        with open(Helpers.CONFIG_PATH, "r") as config:
            contents = json.load(config)

        if contents == Helpers.CONFIG_STRUCT:
            raise Exception("Unconfigured config file.")

        return contents