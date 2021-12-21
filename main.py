#!/usr/bin/env python

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

from argparse import ArgumentParser

from hltb_parser import get_games, parse_games_info, save_games_info, find_similar_games


def parse_args():
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-s",
        "--similar",
        dest="similar",
        action="store_true",
        help="Find similar games from the input list of games.",
    )
    return arg_parser.parse_args()


def main():
    print("Starting HLTB parser..")
    args = parse_args()

    print("Parsing input list of games..")
    games = get_games()

    if args.similar:
        print("Looking for similar games..")
        find_similar_games(games)

        print("All similar games have been found! Thank You for waiting!")
    else:
        print("Parsing games info..")
        games_info = parse_games_info(games)

        print("Saving output games info..")
        save_games_info(games_info)

        print("Parsing finished! Thank You for waiting!")


if __name__ == "__main__":
    main()
