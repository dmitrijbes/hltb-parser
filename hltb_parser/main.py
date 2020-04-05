#! /usr/bin/env python

"""HLTB Parser Main module / Launcher

Main module of the program that starts the program
and re-throws data from module to module.
"""
import sys
from pathlib import Path
module_location = Path(__file__).resolve().parents[1]
sys.path.append(str(module_location))

from hltb_parser.game_input import process_games

process_games()
