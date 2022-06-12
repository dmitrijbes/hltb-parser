# Copyright © 2021 Dima Beskrestnov

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import sep
from urllib import request, parse
from re import sub, search
from re import compile as reg_compile

from bs4 import BeautifulSoup

from levenshtein_distance import is_similar, get_similar_items


def get_games():
    input_games_path = sep.join([".", "input", "games.csv"])
    with open(input_games_path, "r", encoding="utf-8") as input_games_file:
        input_games = input_games_file.read()

    return input_games.splitlines()


def parse_games_info(games):
    games_info = []

    games_processed = 0
    for game in games:
        games_info.append(parse_game_info(game))
        games_processed += 1
        if not games_processed % 100:
            print(str(games_processed), " games already processed!")

    return games_info


def query_hltb(game):
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
    url = "https://howlongtobeat.com/search_results.php"
    query = {
        "queryString": game,
        "t": "games",
        "page": "1",
        "sorthead": "popular",
        "sortd": "Normal Order",
        "plat": "",
        "length_type": "main",
        "length_min": "",
        "length_max": "",
        "detail": "0",
    }

    req = request.Request(url, parse.urlencode(query).encode())
    req.add_header("User-Agent", user_agent)
    req.add_header("Referer", "https://howlongtobeat.com/")
    hltb_response = request.urlopen(req).read()

    return hltb_response


class GameInfo:
    def __init__(self, input_name):
        self.input_name = input_name
        self.sanitized_name = sanitize_name(input_name)
        self.parsed_name = ""
        self.main_length = 0
        self.main_extra_length = 0
        self.completionist_length = 0

    def get_csv_row(self):
        return ",".join(
            [
                self.input_name,
                self.parsed_name,
                str(self.main_length),
                str(self.main_extra_length),
                str(self.completionist_length),
            ]
        )


def trim_whitespaces(input_text):
    """Remove leading and trailing whitespaces. Replace all consequent whitespaces with one space."""

    return " ".join(input_text.split())


def replace_exclude(input_text, replace_text="", exclude_regex="[^a-zA-Z]"):
    """Replace all characters from input_text with provided replace_text, excluding specified in exclude_regex."""

    replace_pattern = reg_compile(exclude_regex)
    return sub(replace_pattern, replace_text, input_text)


def sanitize_name(name):
    return trim_whitespaces(replace_exclude(name.lower(), " ", "[^a-zA-Z0-9]"))


def parse_game_info(game):
    game_info = GameInfo(game)
    hltb_response = query_hltb(game_info.sanitized_name)

    if hltb_response:
        soup = BeautifulSoup(hltb_response, "html.parser")

        if soup.ul:
            response_games = soup.ul.find_all("li")
            get_matching_game_info(response_games, game_info)
        elif soup.li and soup.li.get_text().find("No results for") != -1:
            game_info.parsed_name = "NO_RESULTS_IN_HLTB"

    if not game_info.parsed_name:
        game_info.parsed_name = "FAILED_TO_FIND"

    return game_info


def is_matching_game(response_game_details, game_info):
    sanitized_parsed_name = sanitize_name(response_game_details.a.string)

    return is_similar(game_info.sanitized_name, sanitized_parsed_name, 0.7)


def get_matching_game_info(response_games, game_info):
    for response_game in response_games:
        response_game_details = response_game.find(class_="search_list_details")
        if not is_matching_game(response_game_details, game_info):
            continue

        game_info.parsed_name = response_game_details.a.string

        response_game_length = response_game_details.find_all(class_="center")
        if len(response_game_length) >= 1:
            game_info.main_length = get_length_number(response_game_length[0].string)
        if len(response_game_length) >= 2:
            game_info.main_extra_length = get_length_number(
                response_game_length[1].string
            )
        if len(response_game_length) >= 3:
            game_info.completionist_length = get_length_number(
                response_game_length[2].string
            )


def get_length_number(game_length):
    length = search(r"\d+", game_length)
    if length:
        length_number = float(length.group())

        if game_length.find("Mins") != -1:
            length_number = round((float(length_number) / 60), 2)
        if game_length.find("½") != -1:
            length_number += 0.5
        return length_number

    return 0


def save_games_info(games_info):
    output_games_info_path = sep.join([".", "output", "games_info.csv"])
    with open(output_games_info_path, "w", encoding="utf-8") as games_info_file:
        games_info_file.write(get_game_info_header() + "\n")
        for game_info in games_info:
            games_info_file.write(game_info.get_csv_row() + "\n")


def get_game_info_header():
    game_info_header = (
        "Input Name,Parsed Name,Main Length,Main Extra Length,Completionist Length"
    )

    return game_info_header


def filter_similar_games(similar_games):
    filtered_similar_games = []

    for game_a, game_b in similar_games:
        game_a_parts = game_a.split(" ")
        game_b_parts = game_b.split(" ")
        diff = [i for i in game_a_parts if i not in game_b_parts]

        if not diff:
            continue
        if len(diff) == 1 and diff[0] in (
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
            "IX",
            "X",
            "XI",
            "XII",
            "XIII",
            "XIV",
            "XV",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
        ):
            continue
        filtered_similar_games.append((game_a, game_b))

    return filtered_similar_games


def find_similar_games(games):
    similar_games = get_similar_items(games, 0.60)
    similar_games = filter_similar_games(similar_games)

    output_similar_games_path = sep.join([".", "output", "similar_games.txt"])
    with open(output_similar_games_path, "w", encoding="utf-8") as similar_games_file:
        for similar_game in similar_games:
            similar_games_file.write(similar_game[0] + " <=> " + similar_game[1] + "\n")
