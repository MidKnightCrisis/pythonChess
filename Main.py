import pygame
from collections import namedtuple

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
            currentPos = get_piece(col_idx, row_idx)
            if tile[1].collidepoint(pos) and currentPos != "EM" and turn in currentPos:
                return [tile[1], currentPos, [col_idx, row_idx]]
    return [None, "EM", []]


def move(pos, start):
    global turn
    target = None
    # Finds clicked tile coordinates and current occupation
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            if tile[1].collidepoint(pos):
                target = [tile[1], get_piece(col_idx, row_idx), [col_idx, row_idx]]
                # If clicked tile contains another piece of current player, select that
                # TODO: Edge case Castling
                if turn in target[1]:
                    return target
    if target is None:
        return [None, "EM", []]
    # General Logic in Piece Movement:
    # 1. target tile is within move set of current piece
    # 2. there is no piece obstructing movement
    # 3. target tile is occupiable
    # TODO: Check and Mate
    target_x, target_y = target[2]
    start_x, start_y = start[2]
    if move_check(start_x, start_y, target_x, target_y, start[1]) and check_capture(target[1]):
        return capture(start, target)
    return [None, "EM", []]

def move_check(start_x, start_y, end_x, end_y, piece):
    dx = abs(end_x - start_x)
    dy = abs(end_y - start_y)
    if piece[1] in "RBQ":
        if (piece[1] in "BQ" and dx == dy) or (piece[1] in "RQ" and (dx == 0 or dy == 0)):
            if is_path_clear(start_x, start_y, end_x, end_y):
                return True
    elif ("K" in piece and max(dx, dy) == 1) or ("N" in piece and dx * dy == 2):
        return True
    #Remaining case: Pawn
    else:
        step = 1 if "b" in piece else -1
        start_row = 1 if step == 1 else 6
        # Check 1-step
        if start_y + step == end_y and dx <= 1:
            # TODO: En Passant
            target = get_piece(end_x, end_y)
            if (dx == 1 and turn not in target and target != "EM") or (dx == 0 and target == "EM"):
                return True
        # Check 2-step
        elif start_y + 2 * step == end_y and start_y == start_row:
            for i in range(start_y + step, end_y + step, step):
                if get_piece(start_x, i) != "EM":
                    return False
            return True
    return False

def check_capture(target):
    if target == "EM" or turn not in target:
        return True
    return False

def capture(start, target):
    global turn
    target_x, target_y = target[2]
    start_x, start_y = start[2]
    set_piece(target_x, target_y, start[1])
    set_piece(start_x, start_y, "EM")
    turn = "w" if turn == "b" else "b"
    return [None, "EM", []]

def get_piece(x, y):
    return piecePos[y][x]

def set_piece(x, y, piece):
    piecePos[y][x] = piece

def is_path_clear(start_x, start_y, end_x, end_y):
    step_x = (end_x > start_x) - (end_x < start_x)
    step_y = (end_y > start_y) - (end_y < start_y)
    temp_x = start_x + step_x
    temp_y = start_y + step_y
    while not (temp_x == end_x and temp_y == end_y):
        if get_piece(temp_x,temp_y) != "EM":
            return False
        temp_x += step_x
        temp_y += step_y
    return True

# def get_pseudo_legal_moves():
#     move_list = namedtuple('Move',['start','end','moved','captured','special'])
#
#     return move_list

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