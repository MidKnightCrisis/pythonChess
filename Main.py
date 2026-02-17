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
selected = [None, "EM", ()]
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
                img[piece] = pygame.transform.scale(pygame.image.load(f"Images\\pieces-basic-png\\{piece}.png"),
                                                    (50, 50))
    for yPos in range(8):
        row = []
        for xPos in range(8):
            color = "White" if (xPos + yPos) % 2 == 0 else "Grey"
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            row.append([color, rect])
        board.append(row)


def select_piece(pos):
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            piece = get_piece(col_idx, row_idx)
            if tile[1].collidepoint(pos) and piece != "EM" and turn in piece:
                return [tile[1], piece, (col_idx, row_idx)]
    return [None, "EM", ()]


def move(pos, start):
    global turn
    target = None
    # Finds clicked tile coordinates and current occupation
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            if tile[1].collidepoint(pos):
                target = [tile[1], get_piece(col_idx, row_idx), (col_idx, row_idx)]
                # If clicked tile contains another piece of current player, select that
                # TODO: Edge case Castling
                if turn in target[1]:
                    return target
    if target is None:
        return start
    # General Logic in Piece Movement:
    # 1. target tile is within move set of current piece
    # 2. there is no piece obstructing movement
    # 3. target tile is occupiable
    # TODO: Check and Mate
    target_x, target_y = target[2]
    start_x, start_y = start[2]
    if move_check(start_x, start_y, target_x, target_y, start[1]) and check_capture(target[1]):
        return capture(start_x, start_y, target_x, target_y, start[1])
    return start


def move_check(start_x, start_y, target_x, target_y, piece):
    dx = abs(target_x - start_x)
    dy = abs(target_y - start_y)
    if piece[1] in "RBQ":
        if (piece[1] in "BQ" and dx == dy) or (piece[1] in "RQ" and (dx == 0 or dy == 0)):
            if (target_x, target_y) in slide_ray(start_x, start_y, piece):
                return True
    elif ("K" in piece and max(dx, dy) == 1) or ("N" in piece and dx * dy == 2):
        return True
    # Remaining case: Pawn
    else:
        step = 1 if "b" in piece else -1
        start_row = 1 if step == 1 else 6
        # Check 1-step
        if start_y + step == target_y and dx <= 1:
            # TODO: En Passant
            target = get_piece(target_x, target_y)
            if (dx == 1 and turn not in target and target != "EM") or (dx == 0 and target == "EM"):
                return True
        # Check 2-step
        elif start_y + 2 * step == target_y and start_y == start_row:
            for i in range(start_y + step, target_y + step, step):
                if get_piece(start_x, i) != "EM":
                    return False
            return True
    return False


def check_capture(target):
    if target == "EM" or turn not in target:
        return True
    return False


def capture(start_x, start_y, target_x, target_y, piece):
    global turn
    set_piece(target_x, target_y, piece)
    set_piece(start_x, start_y, "EM")
    turn = "w" if turn == "b" else "b"
    return [None, "EM", ()]


def get_piece(x, y):
    return piecePos[y][x]


def set_piece(x, y, piece):
    piecePos[y][x] = piece


def slide_ray(start_x, start_y, piece):
    moves = []
    directions = []
    if piece[1] in "RQ":
        directions += [(-1, 0), (0, 1), (1, 0), (0, -1)]
    if piece[1] in "BQ":
        directions += [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for dx, dy in directions:
        for i in range(1,8):
            end_x = start_x + dx * i
            end_y = start_y + dy * i
            if 0 <= end_x < 8 and 0 <= end_y < 8:
                target = get_piece(end_x, end_y)
                if target == "EM":
                    moves.append((end_x, end_y))
                elif turn not in target:
                    moves.append((end_x, end_y))
                    break
                else:
                    break
            else:
                break
    return moves


def stepper_check(start_x, start_y, piece):
    moves = []
    knight_jumps = [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]
    king_steps = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, 1), (1, -1), (-1, -1)]
    directions = knight_jumps if "N" in piece else king_steps
    for dx, dy in directions:
        end_x = start_x + dx
        end_y = start_y + dy
        if 0 <= end_x < 8 and 0 <= end_y < 8:
            target = get_piece(end_x, end_y)
            if target == "EM" or turn not in target:
                moves.append((end_x, end_y))
    return moves


def get_pseudo_legal_moves():
    Move = namedtuple('Move',['start','end','moved','captured','special'])
    move_list = []
    for r in range(8):
        for c in range(8):
            p = get_piece(c, r)
            if turn in p:
                match p[1]:
                    # TODO: Special flags for En Passant and Castling
                    case "R"|"B"|"Q":
                        for pos in slide_ray(c, r, p):
                            target = get_piece(pos[0], pos[1])
                            if target == "EM":
                                move_list.append(Move((c, r), pos, p, "EM", "00"))
                            elif turn not in target:
                                move_list.append(Move((c, r), pos, p, target, "00"))
                    case "N"|"K":
                        for pos in stepper_check(c, r, p):
                            target = get_piece(pos[0], pos[1])
                            if target == "EM":
                                move_list.append(Move((c, r), pos, p, "EM", "00"))
                            elif turn not in target:
                                move_list.append(Move((c, r), pos, p, target, "00"))
                    case "P":
                        # TODO: Pawn stuff
                        continue
    return move_list

init()
while run:
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected[0] is None:
                selected = select_piece(event.pos)
            else:
                selected = move(event.pos, selected)
    # wipe last screen
    screen.fill("white")
    # FRONT END CODE
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            pygame.draw.rect(screen, tile[0], tile[1])
            piece = get_piece(col_idx, row_idx)
            if piece != "EM":
                screen.blit(img[piece], tile[1])
    pygame.draw.rect(screen, "Black", pygame.Rect(50, 50, 400, 400), 2)
    if selected[0] is not None:
        pygame.draw.rect(screen, "Red", selected[0], 1)
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
