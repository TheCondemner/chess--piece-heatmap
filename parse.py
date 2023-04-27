import json

def load_pgn(moves):
    # Sets up default board position
    board = [["wR", "wN", "wB1", "wQ", "wK", "wB2", "wN", "wR"],
             ["w"+str(i) for i in list("abcdefgh")],
             [""]*8,
             [""]*8,
             [""]*8,
             [""]*8,
             ["b"+str(i) for i in list("abcdefgh")],
             ["bR", "bN", "bB2", "bQ", "bK", "bB1", "bN", "bR"]]

    # Calculates board from 3 phases of game
    for segment in range(1, 4):

        # Sets up board after each move
        for i, move in enumerate(moves[(segment-1) * len(moves) // 3:segment * len(moves) // 3]):

            # Sanitises algebraic notation to not cause indexing errors from special case characters
            move.replace("x", "")
            if move[-1] in ("+", "#"):
                move = move[:-1]

            # Sets up board after short castle
            if move == "O-O":
                x, y = ("w", 0) if i % 2 == 0 else ("b", 7)
                board[y][4], board[y][5], board[y][6], board[y][7] = "", x+"R", x+"K", ""

            # Sets up board after long castle
            elif move == "O-O-O":
                x, y = ("w", 0) if i % 2 == 0 else ("b", 7)
                board[y][0], board[y][2], board[y][3], board[y][4] = "", x+"R", x+"K", ""

            # Sets up board after any other move
            else:
                # Finds coordinate piece will move to
                _to = (int(move[-1])-1, "abcdefgh".index(move[-2]))

                # Finds coordinates of piece before move
                match move[0]:
                    case "K" | "Q":
                        _from = [(indy, indx) for indy, row in enumerate(board) for indx, p in enumerate(row) if p and p[:2] == ("w" if i % 2 == 0 else "b") + move[0]][0]
                    case "B":
                        piece = "B1" if (_to[0] + _to[1]) % 2 == 0 else "B2"
                        _from = [(indy, indx) for indy, row in enumerate(board) for indx, p in enumerate(row) if p and p[1] == "B" and p == ("w" if i % 2 == 0 else "b") + piece][0]
                    case "N":
                        vectors = [-2, -1, 1, 2]
                        positions = [(_to[0] + indy, _to[1] + indx) for indx in vectors for indy in vectors if abs(indx) != abs(indy) and 0 <= _to[0] + indy <= 7 and 0 <= _to[1] + indx <= 7]
                        pieces = [pos for pos in positions if board[pos[0]][pos[1]] and board[pos[0]][pos[1]][:2] == (("w" if i % 2 == 0 else "b") + "N")]
                        _from = pieces[0] if len(pieces) == 1 else ([pos for pos in pieces if move[1] in (pos[0], "abcdefgh"[pos[1]])][0])
                    case "R":
                        positions = [(indy, indx) for indy, row in enumerate(board) for indx, p in enumerate(row) if p and p[:2] == ("w" if i % 2 == 0 else "b") + "R" and (indy == _to[0] or indx == _to[1])]
                        if len(positions) > 1:
                            positions = [pos for pos in positions if (pos[0] == _to[0] and not any(board[pos[0]][slice(pos[1]+1, _to[1]) if pos[1] < _to[1] else slice(_to[1]+1, pos[1])])) or (pos[1] == _to[1] and any([y for x in board for indy, y in enumerate(x) if indy == pos[1]][slice(pos[0]+1, _to[0]) if pos[0] < _to[0] else slice(_to[0]+1, pos[0])]))]
                        if len(positions) == 1:
                            _from = positions[0]
                        elif positions[0][1] == positions[1][1]:
                            _from = (_to[0], int(move[1])-1)
                        else:
                            _from = (positions[0][0], "abcdefgh".index(move[1]))
                    case _:
                        _from = (_to[0] + 2*(i % 2) - 1, "abcdefgh".index(move[0]))
                        if not board[_from[0]][_from[1]]:
                            _from = (_from[0] + 2*(i % 2) - 1, _from[1])

                # Updates board with new positions
                board[_to[0]][_to[1]], board[_from[0]][_from[1]] = board[_from[0]][_from[1]], ""

        yield board

games = json.load(open("games.json", "r"))["games"]
print(games)

with open("boards.json", "w") as f:
    boards = []

    for game in games:
        try:
            boards.append(list(load_pgn(game["moves"])))
        except:
            pass

    print(boards)
    
    json.dump(boards, f)
