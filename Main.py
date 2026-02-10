import pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
# delta time (s) since last frame; useful for frame-independent physics
dt = 0
# current tile color
# aMap = ["a","b","c","d","e","f","g","h"]
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
    for yPos in range(8):
        row = []
        for xPos in range(8):
            color = "White" if (xPos + yPos) % 2 == 0 else "Grey"
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            row.append([color, rect])
        board.append(row)
def selectpiece(pos):
    for yPos in board:
        row = board.index(yPos)
        for xPos in yPos:
            col = yPos.index(xPos)
            currentPos = piecePos[row][col]
            if xPos[1].collidepoint(pos) and currentPos != "EM" and turn in currentPos:
                print([xPos[1], currentPos, [col, row]])
                return [xPos[1], currentPos, [col, row]]
    return [None, "EM", []]


def move(pos, start):
    coords = None
    target = None
    # Finds clicked tile coordinates and current occupation
    for row in board:
        row_index = board.index(row)
        for col in row:
            col_index = row.index(col)
            if col[1].collidepoint(pos):
                coords = [col_index, row_index]
                target = piecePos[row_index][col_index]
                # If clicked tile contains another piece of current player, select that
                # TODO: Edge case Castling
                if turn in target:
                    return [col[1], target, coords]
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
            if target == "EM" or turn not in target:
                piecePos[coords[1]][coords[0]] = start[1]
                piecePos[start[2][1]][start[2][0]] = "EM"
                return [None, "EM", []]
            # This case should only be for target tile having current player's piece
            else:
                return [None, "EM", []]
        else:
            step = 1 if coords[0] > start[2][0] else -1
            for i in range(start[2][0] + step, coords[0], step):
                if piecePos[coords[1]][i] != "EM":
                    return [None, "EM", []]
            if target == "EM" or turn not in target:
                piecePos[coords[1]][coords[0]] = start[1]
                piecePos[start[2][1]][start[2][0]] = "EM"
                return [None, "EM", []]
            # This case should only be for target tile having current player's piece
            else:
                return [None, "EM", []]
    elif "P" in start[1]:
        step = 1 if "b" in start[1] else -1
        opponent = "w" if step == 1 else "b"
        srow = 1 if step == 1 else 6
        # Check 1-step
        print(start[2][1])
        print(step)
        print(coords[1])
        if start[2][1] + step == coords[1] and abs(coords[0] - start[2][0]) <= 1:
            if (abs(coords[0] - start[2][0]) == 1 and opponent in target) or (abs(coords[0] - start[2][0]) == 0 and target == "EM"):
                piecePos[coords[1]][coords[0]] = start[1]
                piecePos[start[2][1]][start[2][0]] = "EM"
                return [None, "EM", []]
            else:
                return [None, "EM", []]
        # Check 2-step
        elif start[2][1] + 2 * step == coords[1] and start[2][1] == srow:
            for i in range(start[2][1] + step, coords[1] + step, step):
                if piecePos[i][start[2][0]] != "EM":
                    return [None, "EM", []]
            piecePos[coords[1]][coords[0]] = start[1]
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
    for row in board:
        row_index = board.index(row)
        for tile in row:
            tile_index = row.index(tile)
            pygame.draw.rect(screen,tile[0],tile[1])
            curpiece = piecePos[row_index][tile_index]
            if curpiece != "EM":
                screen.blit(pygame.transform.scale(pygame.image.load(f"Images\\pieces-basic-png\\{curpiece}.png"),(50,50)), tile[1])
    pygame.draw.rect(screen, "Black", pygame.Rect(50, 50, 400, 400), 2)
    if selected[0] is not None:
        pygame.draw.rect(screen, "Red", selected[0], 1)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()