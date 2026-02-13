import pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
# delta time (s) since last frame; useful for frame-independent physics
dt = 0
# current tile color
# aMap = ["a","b","c","d","e","f","g","h"]
img = {}
turn = "w"
board = []
selected = [None, "EM", []]
# check if current piece is white
piecePos = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
    ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
    ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
    ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
]

def init():
    for row in piecePos:
        for piece in row:
            if piece != "EM" and piece not in img:
                img[piece] = pygame.transform.scale(pygame.image.load(f"Images\\pieces-basic-png\\{piece}.png"),(50,50))
    for yPos in range(8):
        row = []
        for xPos in range(8):
            color = "White" if (xPos + yPos) % 2 == 0 else "Grey"
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            row.append([color, rect])
        board.append(row)
def selectpiece(pos):
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            currentPos = piecePos[row_idx][col_idx]
            if tile[1].collidepoint(pos) and currentPos != "EM" and turn in currentPos:
                return [tile[1], currentPos, [col_idx, row_idx]]
    return [None, "EM", []]


def move(pos, start):
    coords = None
    target = None
    # Finds clicked tile coordinates and current occupation
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            if tile[1].collidepoint(pos):
                coords = [col_idx, row_idx]
                target = piecePos[row_idx][col_idx]
                # If clicked tile contains another piece of current player, select that
                # TODO: Edge case Castling
                if turn in target:
                    return [tile[1], target, coords]
    if coords is None:
        return [None, "EM", []]
    # General Logic in Piece Movement:
    # 1. target tile is within move set of current piece
    # 2. there is no piece obstructing movement
    # 3. target tile is occupiable
    # TODO: Check and Mate
    if "R" in start[1]:
        if not (coords[0] == start[2][0] or coords[1] == start[2][1]):
            return [None, "EM", []]
        elif coords[0] == start[2][0]:
            step = 1 if coords[1] > start[2][1] else -1
            for i in range(start[2][1]+step, coords[1], step):
                if piecePos[i][coords[0]] != "EM":
                    return [None, "EM", []]
            return checkCapture(coords, start, target)
        else:
            step = 1 if coords[0] > start[2][0] else -1
            for i in range(start[2][0] + step, coords[0], step):
                if piecePos[coords[1]][i] != "EM":
                    return [None, "EM", []]
            return checkCapture(coords, start, target)
    elif "P" in start[1]:
        step = 1 if "b" in start[1] else -1
        opponent = "w" if step == 1 else "b"
        srow = 1 if step == 1 else 6
        # Check 1-step
        if start[2][1] + step == coords[1] and abs(coords[0] - start[2][0]) <= 1:
            # TODO: En Passant
            if (abs(coords[0] - start[2][0]) == 1 and opponent in target) or (abs(coords[0] - start[2][0]) == 0 and target == "EM"):
                piecePos[coords[1]][coords[0]] = start[1]
                piecePos[start[2][1]][start[2][0]] = "EM"
            return [None, "EM", []]
        # Check 2-step
        elif start[2][1] + 2 * step == coords[1] and start[2][1] == srow:
            for i in range(start[2][1] + step, coords[1] + step, step):
                if piecePos[i][start[2][0]] != "EM":
                    return [None, "EM", []]
            piecePos[coords[1]][coords[0]] = start[1]
            piecePos[start[2][1]][start[2][0]] = "EM"
        return [None, "EM", []]
    elif "B" in start[1]:
        if not abs(coords[0] - start[2][0]) == abs(coords[1] - start[2][1]):
            return [None, "EM", []]
        else:
            stepX = 1 if coords[0] > start[2][0] else -1
            stepY = 1 if coords[1] > start[2][1] else -1
            for i in range(1, abs(coords[0]-start[2][0])):
                if piecePos[start[2][1] + i * stepY][start[2][0] + i * stepX] != "EM":
                    return [None, "EM", []]
            return checkCapture(coords, start, target)
    elif "Q" in start[1]:
        if not (coords[0] == start[2][0] or coords[1] == start[2][1] or abs(coords[0] - start[2][0]) == abs(coords[1] - start[2][1])):
            return [None, "EM", []]
        elif abs(coords[0] - start[2][0]) == abs(coords[1] - start[2][1]):
            stepX = 1 if coords[0] > start[2][0] else -1
            stepY = 1 if coords[1] > start[2][1] else -1
            for i in range(1, abs(coords[0] - start[2][0])):
                if piecePos[start[2][1] + i * stepY][start[2][0] + i * stepX] != "EM":
                    return [None, "EM", []]
            return checkCapture(coords, start, target)
        elif coords[0] == start[2][0]:
            step = 1 if coords[1] > start[2][1] else -1
            for i in range(start[2][1]+step, coords[1], step):
                if piecePos[i][coords[0]] != "EM":
                    return [None, "EM", []]
            return checkCapture(coords, start, target)
        else:
            step = 1 if coords[0] > start[2][0] else -1
            for i in range(start[2][0] + step, coords[0], step):
                if piecePos[coords[1]][i] != "EM":
                    return [None, "EM", []]
            return checkCapture(coords, start, target)
    elif "K" in start[1]:
        # TODO: Castling
        if not (abs(coords[0] - start[2][0]) <= 1 and abs(coords[1] - start[2][1]) <= 1):
            return [None, "EM", []]
        return checkCapture(coords, start, target)
    else:
        if not ((abs(coords[0] - start[2][0]) == 2 and abs(coords[1] - start[2][1]) == 1) or(abs(coords[0] - start[2][0]) == 1 and abs(coords[1] - start[2][1]) == 2)):
            return [None, "EM", []]
        return checkCapture(coords, start, target)



def checkCapture(coord, start, target):
    if target == "EM" or turn not in target:
        piecePos[coord[1]][coord[0]] = start[1]
        piecePos[start[2][1]][start[2][0]] = "EM"
        return [None, "EM", []]
    else:
        return [None, "EM", []]

init()
while run:
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected[0] is None:
                selected = selectpiece(event.pos)
            else:
                selected = move(event.pos, selected)
    # wipe last screen
    screen.fill("white")
    # FRONT END CODE
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            pygame.draw.rect(screen,tile[0],tile[1])
            curpiece = piecePos[row_idx][col_idx]
            if curpiece != "EM":
                screen.blit(img[curpiece], tile[1])
    pygame.draw.rect(screen, "Black", pygame.Rect(50, 50, 400, 400), 2)
    if selected[0] is not None:
        pygame.draw.rect(screen, "Red", selected[0], 1)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()