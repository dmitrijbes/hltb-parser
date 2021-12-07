# HLTB Parser
Simple howlongtobeat.com parser.

## How to Run
1\. Download or Fork source code.  
2\. Install dependencies:
```
pip install beautifulsoup4
```
3\. Add list of targeted games into 'input/games.csv' file. Single game per line.  
4\. Run:
```
python main.py
```
5\. Get result from 'output' folder.

### etc.
Use '--similar' argument to find similar games from the input list of games.
```
python main.py --similar
```

## License
Apache License 2.0  
In short, your are free to use (including commercial), copy, modify, dance, distribute.
