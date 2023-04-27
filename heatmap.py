# -------------------------------------------------------- #
#                          IMPORTS                         #
# -------------------------------------------------------- #
import numpy as np
import matplotlib.pyplot as plt
import json

# -------------------------------------------------------- #
#                          CONFIG                          #
# -------------------------------------------------------- #
codes = ["R", "N", "B1", "B2", "Q", "K", "a", "b", "c", "d", "e", "f", "g", "h"]
labels = {
    "Rooks"   : ["R"],
    "Knights" : ["N"],
    "Bishops" : ["B1", "B2"],
    "Queen"   : ["Q"],
    "King"    : ["K"],
    "Pawn"    : ["a", "b", "c", "d", "e", "f", "g", "h"]
}

# -------------------------------------------------------- #
#                         FUNCTIONS                        #
# -------------------------------------------------------- #
def getPieceMap(board, code):
    if not (code or len(code) or code[1:] in codes):
        print(f"Invalid input to getPieceMap() {code}")
        return None

    map = []
    for i, row in enumerate(board):
        map.append([])
        for square in row:
            if square == code:
                map[i].append(1)
            else:
                map[i].append(0)
    
    return map

# -------------------------------------------------------- #
#                          RUNTIME                         #
# -------------------------------------------------------- #
boards = json.load(open("boards.json", "r"))
images = []

fig, axs = plt.subplots(6, len(labels.items()))
fig.suptitle("Chess Piece Heatmaps")

for time in range(3):        
    for color in ["w", "b"]:
        rint=(time*2)+(0 if color=="w" else 1)

        print(color, time, rint)

        for label, pieces in labels.items():
            itemindex = list(labels.keys()).index(label)
            map = np.zeros((8, 8))

            for piece in pieces:
                for board in boards:
                    map += np.array(getPieceMap(board[time], color+piece))

            images.append(axs[rint, itemindex].imshow(map, cmap="viridis"))

            axs[rint, itemindex].yaxis.set_ticks(np.arange(0, 8, 1))
            axs[rint, itemindex].xaxis.set_ticks(np.arange(0, 8, 1))

            axs[rint, itemindex].label_outer()
            axs[rint, itemindex].set_title(f"{['Start', 'Middle', 'End'][time]} {'White' if color=='w' else 'Black'} {label}", {"fontsize": 8})

vmin = min([np.min(image.get_array()) for image in images])
vmax = max([np.max(image.get_array()) for image in images])

fig.colorbar(images[0], ax=axs, orientation="horizontal", fraction=0.06, pad=0.08)  

plt.show()