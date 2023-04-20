# ---------------------------------- IMPORTS --------------------------------- #
from chessdotcom import client as chess
import json, os, urllib.request, re, random

# --------------------------------- VARIABLES -------------------------------- #
REGENERATE  = False # Re-generate all files, even if they already exist
RANDSEED    = 11111

MAXPLAYERS  = 2
TARGETGAMES = 50
GAMECRITERIA = {                        # Setting any to None will have them be ignored
    "elo_avg"  : 1500,                  # int
    "elo_diff" : 100,                   # int
    "type"     : ["chess"],             # array[] : string
    "time"     : ["classical", "rapid"] # array[] : string
}

# ---------------------------------- RUNTIME --------------------------------- #
random.seed(RANDSEED)

# Get Player List
players = chess.get_country_players("ES").json["players"]
print("Pre-shuffle", len(players))
random.shuffle(players)
players = players[:MAXPLAYERS]
print("Post-shuffle", len(players), *players)

# Get Game Archives
archives = []
if os.path.exists("archives.json") and not REGENERATE:
    with open("archives.json", "r") as f:
        print("Loading archives from file...")
        archives = json.load(f)
        print("Loaded archives from file")
else:
    for player in players:
        archives = [*archives, *chess.get_player_game_archives(player).json["archives"]]
    random.shuffle(archives) # Prevent all archives from being from the same month / player / etc.

    with open("archives.json", "w") as f:
        print("Generating archive file...")
        json.dump(archives, f)   
        print("Generated archive file") 

# Get Games
games = []
# if os.path.exists("games.json") and not REGENERATE:
#     with open("games.json", "r") as f:
#         print("Loading games from file...")
#         games = json.load(f)
# else:
for archive in archives:
    print("Opening archive", archive)
    gameManifest = json.loads(urllib.request.urlopen(archive).read())["games"]
    result = []

    for game in gameManifest:
        formatted = {
            "moves"      : re.findall(r"(?<=[1-9]\. )(.*?)(?= {)", game["pgn"]),
            "move_count" : len(re.findall(r"(?<=[1-9]\. )(.*?)(?= {)", game["pgn"])),
            "time"       : game["time_class"],
            "type"       : game["rules"],
            "rate"       : game["rated"],
            "elo_avg" : (game["white"]["rating"] + game["black"]["rating"]) / 2,
            "elo_diff": abs(game["white"]["rating"] - game["black"]["rating"])
        }

        # Check if game meets criteria
        # Only count properly finished games
        if game["white"]["result"] in ["abandoned", "resigned", "outoftime"]: continue
        if game["black"]["result"] in ["abandoned", "resigned", "outoftime"]: continue
        # Check that game within criteria
        if (GAMECRITERIA["type"] is not None) and (formatted["type"] not in GAMECRITERIA["type"]): continue
        if (GAMECRITERIA["time"] is not None) and (formatted["time"] not in GAMECRITERIA["time"]): continue
        if (GAMECRITERIA["elo_avg"] is not None) and (formatted["elo_avg"] < GAMECRITERIA["elo_avg"]): continue
        if (GAMECRITERIA["elo_diff"] is not None) and (formatted["elo_diff"] < GAMECRITERIA["elo_diff"]): continue

        # Add the result
        result.append(formatted)

    games = [*games, *result]

random.shuffle(games)
games = games[:TARGETGAMES]

# Warn if insufficient games found
if len(games) < TARGETGAMES:
    print(f"WARNING: Not enough games were found: {len(games)} out of {TARGETGAMES}\nRegeneration is recommended.")

with open("games.json", "w") as f:
    print("Generating game file...")
    json.dump(games, f)
    print("Generated game file")
