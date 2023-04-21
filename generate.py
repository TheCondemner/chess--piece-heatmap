# -------------------------------------------------------- #
#                          IMPORTS                         #
# -------------------------------------------------------- #
from chessdotcom import client as chess
import json, os, urllib.request, re, random, multiprocessing, time

# -------------------------------------------------------- #
#                         VARIABLES                        #
# -------------------------------------------------------- #
REGENERATE   = False # Re-generate archive cache each run
RANDSEED     = None  # Set to None to get random values each time
PROCESSCOUNT = 6     # Number of processes to use

PLAYERS      = 100   # Number of players to get games
TARGETGAMES  = 10000 # Number of games to get in total
GAMEOVERFLOW = 5     # How many extra games to get per archive (compensation for archives that lack games that fit criteria)

GAMECRITERIA = { # Setting any to None will have them be ignored
    "elo_avg"  : 1000,                   # int ; average elo of players
    "elo_diff" : 100,                    # int ; max difference between players' elo
    "type"     : ["chess"],              # array[] : string
    "time"     : ["classical", "rapid"], # array[] : string
    "move_count" : 20,                   # int ; minimum number of moves
    "rated"    : True                    # bool
}

archives = []
games = []

# -------------------------------------------------------- #
#                         FUNCTIONS                        #
# -------------------------------------------------------- #
def get_game_archives(player):
    try:
        global archives
        playerArchives = chess.get_player_game_archives(player).json["archives"]
        print(f"Found {len(playerArchives)} archives for {player}")
        return playerArchives
    except:
        print(f"Failed to load archives for {player}")

    print("Opening archive", archive)    
    gameManifest = json.loads(urllib.request.urlopen(archive).read())["games"]
    random.shuffle(gameManifest)
    print("Found", len(gameManifest), "games in archive")

    res = []

    for game in gameManifest:
        try:
            formatted = {
                "moves"      : re.findall(r"(?<=[1-9]\. )(.*?)(?= {)", game["pgn"]),
                "move_count" : len(re.findall(r"(?<=[1-9]\. )(.*?)(?= {)", game["pgn"])),
                "time"       : game["time_class"],
                "type"       : game["rules"],
                "rated"      : game["rated"],
                "elo_avg"    : (game["white"]["rating"] + game["black"]["rating"]) / 2,
                "elo_diff"   : abs(game["white"]["rating"] - game["black"]["rating"])
            }
            # print(formatted)

            # Only count properly finished games
            if (game["white"]["result"] in ["abandoned", "resigned", "outoftime"]) or (game["black"]["result"] in ["abandoned", "resigned", "outoftime"]): continue
            # Check that game within criteria
            if GAMECRITERIA.get("elo_avg")    and formatted["elo_avg"]    < GAMECRITERIA["elo_avg"]:    continue
            if GAMECRITERIA.get("elo_diff")   and formatted["elo_diff"]   > GAMECRITERIA["elo_diff"]:   continue
            if GAMECRITERIA.get("time")       and formatted["time"]  not in GAMECRITERIA["time"]:       continue
            if GAMECRITERIA.get("type")       and formatted["type"]  not in GAMECRITERIA["type"]:       continue
            if GAMECRITERIA.get("move_count") and formatted["move_count"] < GAMECRITERIA["move_count"]: continue
            if GAMECRITERIA.get("rated")      and formatted["rated"]     != GAMECRITERIA["rated"]:      continue
            # Add the result
            if len(result) < archiveGameTarget:
                result.append(formatted)
        except:
            print("Failed to load game", game["url"])

        games = [*games, *result] 

        print("Found", len(result), "games that fit criteria")
        print(f"Total {len(games)}")

        if len(games) >= TARGETGAMES:
            break

        print("Failed to load game", game["url"])


# -------------------------------------------------------- #
#                          RUNTIME                         #
# -------------------------------------------------------- #
if __name__ == "__main__":
    random.seed(RANDSEED)

    # ------------------- GET GAME ARCHIVES ------------------ #
    if os.path.exists("archives.json") and not REGENERATE:
        with open("archives.json", "r") as f:
            print("Loading archives from file...")
            archives = json.load(f)
            print("Loaded archives from file")
    else:
        # Get Player List
        players = chess.get_country_players("ES").json["players"]
        random.shuffle(players)
        players = players[:PLAYERS]
        print(f"Found {len(players)} players")

        chess.get_player_game_archives(players[0]).json["archives"]

        # Set-up multiprocessing
        pool = multiprocessing.Pool(PROCESSCOUNT)
        res = pool.map(get_game_archives, players, chunksize=1)
        pool.close()
        pool.join()

        # Parse results
        for archiveList in res:
            if archiveList:
                archives = [*archives, *archiveList]
        random.shuffle(archives)
        print(f"Found {len(archives)} archives")

        # Write to file
        with open("archives.json", "w") as f:
            print("Generating archive file...")
            json.dump(archives, f)   
            print("Generated archive file") 

    # ----------------------- GET GAMES ---------------------- #
    archiveGameTarget = TARGETGAMES // len(archives) + GAMEOVERFLOW
    print("Targeting", archiveGameTarget, "games per archive")

    for archive in archives:
        print("Opening archive", archive)
        gameManifest = json.loads(urllib.request.urlopen(archive).read())["games"]
        random.shuffle(gameManifest)

        print("Found", len(gameManifest), "games in archive")

        result = []

        for game in gameManifest:
            try:
                formatted = {
                    "moves"      : re.findall(r"(?<=[1-9]\. )(.*?)(?= {)", game["pgn"]),
                    "move_count" : len(re.findall(r"(?<=[1-9]\. )(.*?)(?= {)", game["pgn"])),
                    "time"       : game["time_class"],
                    "type"       : game["rules"],
                    "rated"      : game["rated"],
                    "elo_avg"    : (game["white"]["rating"] + game["black"]["rating"]) / 2,
                    "elo_diff"   : abs(game["white"]["rating"] - game["black"]["rating"])
                }
                # print(formatted)

                # Only count properly finished games
                if (game["white"]["result"] in ["abandoned", "resigned", "outoftime"]) or (game["black"]["result"] in ["abandoned", "resigned", "outoftime"]): continue
                # Check that game within criteria
                if GAMECRITERIA.get("elo_avg")    and formatted["elo_avg"]    < GAMECRITERIA["elo_avg"]:    continue
                if GAMECRITERIA.get("elo_diff")   and formatted["elo_diff"]   > GAMECRITERIA["elo_diff"]:   continue
                if GAMECRITERIA.get("time")       and formatted["time"]  not in GAMECRITERIA["time"]:       continue
                if GAMECRITERIA.get("type")       and formatted["type"]  not in GAMECRITERIA["type"]:       continue
                if GAMECRITERIA.get("move_count") and formatted["move_count"] < GAMECRITERIA["move_count"]: continue
                if GAMECRITERIA.get("rated")      and formatted["rated"]     != GAMECRITERIA["rated"]:      continue
                # Add the result
                if len(result) < archiveGameTarget:
                    result.append(formatted)
            except:
                print("Failed to load game", game["url"])

        games = [*games, *result] 

        print("Found", len(result), "games that fit criteria")
        print(f"Total {len(games)}")

        if len(games) >= TARGETGAMES:
            break

        print("Failed to load game", game["url"])

    random.shuffle(games)
    games = games[:TARGETGAMES]

    # Warn if insufficient games found
    if len(games) < TARGETGAMES:
        print(f"WARNING: Not enough games were found: {len(games)} out of {TARGETGAMES}\nRegeneration is recommended.")

    with open("games.json", "w") as f:
        print("Generating game file...")
        json.dump(games, f)
        print("Generated game file")
