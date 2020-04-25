# -*- coding: utf-8 -*-

"""Games Parser

Loads input file and parses it to game list.
Parse HowLongToBeat for games
"""

# Requirement: BeatifulSoup4
# TODO: Implement using setup.py/requirement.txt

from bs4 import BeautifulSoup

import re
import urllib.request

from html.parser import HTMLParser

from general_library.serialization_library.serializer import Serializer
from general_library.formatting_library.formatter import Formatter
from general_library.formatting_library.formats.csv_formatter import CSVFormatter
from general_library.configuration_library import config
from general_library.formatting_library import formatting_utils
from general_library.string_library.levenshtein_distance import get_similar_items
from general_library.string_library.levenshtein_distance import is_similar


def replace_except(input_line, replace_line = "", except_pattern = "[^a-zA-Z]"):
    """Replaces special symbols to specified substring"""

    replace_pattern = re.compile(except_pattern)
    return re.sub(replace_pattern, replace_line, input_line)

def trim_whitespaces(input_line: str):
    """Replaces all consequent whitespace characters with one space"""

    return " ".join(input_line.split())

def sanitize_name(game_name):
    return trim_whitespaces(replace_except(game_name.lower(), " ", '[^a-zA-Z0-9]'))


def find_similar_games(games_list_name):
    games_list = Serializer(games_list_name, config.RESOURCES_FOLDER).deserialize()
    games_dictionary = formatting_utils.from_csv(games_list, ",")
    games_list = []
    for game in games_dictionary:
        games_list.append(game["Name"])
    similar_games = get_similar_items(games_list, 0.60)
    for tested_game, similar_game in similar_games:
        print("Found potentially similar games: ", tested_game, " , ", similar_game)


def get_games_list(games_list_name):
    games_csv = Serializer(games_list_name, config.RESOURCES_FOLDER).deserialize()
    games_parsed_csv = formatting_utils.from_csv(games_csv, ",")
    games_list = []
    for game_parsed_csv in games_parsed_csv:
        games_list.append(game_parsed_csv["Name"])
    return games_list

class GameInfo():
    def __init__(self):
        self.game_name_list = ""
        self.game_name_parsed = ""
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

def get_games_info(games_list):
    games_info = []

    games_processed = 0
    for game in games_list:
        games_info.append(get_game_info(game))
        games_processed += 1
        if not games_processed % 100:
            print(str(games_processed), "games already processed!")

    return games_info

def get_valid_response_game(response_games, game_info, sanitized_name, is_similarity_check):
    for response_game in response_games:
        response_game_details = response_game.find(class_="search_list_details")
        response_game_name = response_game_details.a.string
        sanitized_response_game_name = sanitize_name(response_game_name)

        is_valid_response_game = False
        if is_similarity_check:
            if is_similar(sanitized_name, sanitized_response_game_name, 0.7):
                is_valid_response_game = True
        elif sanitized_response_game_name.find(sanitized_name) != -1 or sanitized_name.find(sanitized_response_game_name) != -1:
            is_valid_response_game = True

        if is_valid_response_game:
            game_info.game_name_parsed = response_game_name

            response_game_time = response_game_details.find_all(class_="center")
            if len(response_game_time) >= 1:
                game_info.main_length = get_length_number(response_game_time[0].string)
            if len(response_game_time) >= 2:
                game_info.main_extra_length = get_length_number(response_game_time[1].string)
            if len(response_game_time) == 3:
                game_info.completionist_length = get_length_number(response_game_time[2].string)
            return True;

    return False;

def get_game_info(game):
    print(game)
    game_info = GameInfo()
    game_info.game_name_list = game
    game_info.game_name_parsed = "FAIL_TO_FIND"

    sanitized_name = sanitize_name(game)
    hltb_html = query_hltb(sanitized_name)
    if hltb_html:
        soup = BeautifulSoup(hltb_html, 'html.parser')
        if soup.ul:
            response_games = soup.ul.find_all("li")
            if response_games:
                if get_valid_response_game(response_games, game_info, sanitized_name, True):
                    return game_info
                elif len(game) > 4 and get_valid_response_game(response_games, game_info, sanitized_name, False):
                    return game_info

        elif soup.li:
            if soup.li.get_text().find("No results for") != -1:
                game_info.game_name_parsed = "NO_RESULTS_IN_HLTB"

    return game_info

def get_length_number(game_length):
    number = re.search(r'\d+', game_length)
    if number:
        number = float(number.group())
        if game_length.find("Mins") != -1:
            number = round((float(number)/60), 2)
        if game_length.find("½") != -1:
            number += 0.5
        return number
    return 0

def query_hltb(game):
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
    html = urllib.request.urlopen(req).read()

    return html

def get_games_length(games_list_name):
    games_list = get_games_list(games_list_name)
    games_info = get_games_info(games_list)

    formatter = Formatter(CSVFormatter())
    formatter << GameInfo().get_csv_header()
    for game_info in games_info:
        formatter << game_info.get_csv_row()
    Serializer("games_info").serialize(formatter)
