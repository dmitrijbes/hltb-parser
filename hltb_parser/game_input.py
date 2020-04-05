# -*- coding: utf-8 -*-

"""Games Parser

Loads input file and parses it to game list.
Parse HowLongToBeat for games
"""

import re
import urllib.request

from html.parser import HTMLParser

# Replaceable symbols
REPLACE_SYMBOLS = ["\\", "/", "`", "*", "_", "{", "}", "[", "]", "(", ",",
                   ")", ">", "#", "+", "-", ".", "!", "$", "\'", "\""]

def replace_special_symbols(input_line: str, replace_line: str = ""):
    """Replaces special symbols to specified substring"""

    for symbol in REPLACE_SYMBOLS:
        if symbol in input_line:
            input_line = input_line.replace(symbol, replace_line)

    return input_line

def trim_whitespaces(input_line: str):
    """Replaces all consequent whitespace characters with one space"""

    return " ".join(input_line.split())

def get_unique_games_list():
    # games_list = Serializer("gamesList.csv", config.RESOURCES_FOLDER).deserialize()
    games_dictionary = formatting_utils.from_csv(games_list, ",", {"Name"})
    unique_games_dictionary = {}
    for game in games_dictionary:
        formatted_game_name = trim_whitespaces(replace_special_symbols(game["Name"].lower(), " "))
        if formatted_game_name in unique_games_dictionary:
            print(f"Looks like this game is already in list: {formatted_game_name}")
        else:
            unique_games_dictionary[formatted_game_name] = True
    return list(unique_games_dictionary.keys())


class GameInfo():
    def __init__(self):
        self.game_parsed_name = ""
        self.game_list_name = ""
        self.main_length = 0
        self.main_extra_length = 0
        self.completionist_length = 0

    def get_csv_row(self, delimiter=","):
        row = ""

        for value in self.__dict__.values():
            if row:
                row += delimiter
            row += '"' + str(value) + '"'

        return row

    def get_csv_header(self, delimiter=","):
        header = ""

        for key in self.__dict__.keys():
            if header:
                header += delimiter
            header += key

        return header


def get_number(string):
    number = re.search(r'\d+', string)
    if number:
        number = number.group()
        if string.find("Mins") != -1:
            number = round((int(number)/60), 2)
        return number
    return ""


def get_games_info(games_list):
    games_info = {}
    games_processed = 0
    for game in games_list:
        game_parsed_info = get_game_length(game)

        game_info = GameInfo()
        game_info.game_list_name = game
        if(len(game_parsed_info) >= 7):  # General case
            game_info.game_parsed_name = game_parsed_info[0]
            game_info.main_length = get_number(game_parsed_info[2])
            game_info.main_extra_length = get_number(game_parsed_info[4])
            game_info.completionist_length = get_number(game_parsed_info[6])
        elif(len(game_parsed_info) >= 3):  # Solo like The Wolf Among Us
            game_info.game_parsed_name = game_parsed_info[0]
            game_info.main_extra_length = get_number(game_parsed_info[2])

        games_info[game] = game_info

        games_processed = games_processed + 1
        if not games_processed % 100:
            print(str(games_processed) + " games already processed!")

    return games_info


class HLTB_HTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_count = 0
        self.tag = "div"
        self.data = []
        self.first_game = True

    def handle_starttag(self, tag, attributes):
        if self.first_game is False:
            return
        if tag != self.tag:
            return
        if self.tag_count:
            self.tag_count += 1
            return
        for name, value in attributes:
            if name == "class" and value == "search_list_details":
                break
        else:
            return
        self.tag_count = 1

    def handle_endtag(self, tag):
        if tag == self.tag and self.tag_count:
            self.tag_count -= 1
            if self.tag_count == 0:
                self.first_game = False

    def handle_data(self, data):
        if self.tag_count and data != " " and data != "\n":
            self.data.append(data)


def get_game_length(game):
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
    url = "https://howlongtobeat.com/search_results.php"
    query = {'queryString': game,
             't': 'games',
             'page': '1',
             'sorthead': 'popular',
             'sortd': 'Normal Order',
             'plat': '',
             'length_type': 'main',
             'length_min': '',
             'length_max': '',
             'detail': '0'}
    req = urllib.request.Request(url, urllib.parse.urlencode(query).encode())
    req.add_header("User-Agent", user_agent)
    html = urllib.request.urlopen(req).read().decode('utf-8')
    parser = HLTB_HTMLParser()
    parser.feed(html)
    return parser.data


def process_games():
    games_list = get_unique_games_list()
    games_info = get_games_info(games_list)

    # formatter = Formatter(CSVFormatter())
    # formatter << GameInfo().get_csv_header()
    # for game_info in games_info.values():
    #     formatter << game_info.get_csv_row()
    # Serializer("games_info").serialize(formatter)
