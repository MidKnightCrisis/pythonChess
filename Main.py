import pygame
from collections import namedtuple

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
# delta time (s) since last frame; useful for frame-independent physics
dt = 0
img = {}
turn = "w"
board = []
selected = [None, "EM", ()]
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


def move(pos, start, pseudo_moves):
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
    if any(m.start == start[2] and m.target == target[2] for m in pseudo_moves):
        return capture(start[2], target[2], start[1])
    return start


def capture(start, target, piece):
    global turn, pl_moves
    start_x, start_y = start
    target_x, target_y = target
    set_piece(target_x, target_y, piece)
    set_piece(start_x, start_y, "EM")
    pl_moves = get_pseudo_legal_moves()
    turn = "w" if turn == "b" else "b"
    return [None, "EM", ()]


def get_piece(x, y):
    return piecePos[y][x]


def set_piece(x, y, piece):
    piecePos[y][x] = piece


def slide_ray(start, piece):
    start_x, start_y = start
    moves = []
    directions = []
    if piece[1] in "RQ":
        directions += [(-1, 0), (0, 1), (1, 0), (0, -1)]
    if piece[1] in "BQ":
        directions += [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for dx, dy in directions:
        for i in range(1,8):
            target_x = start_x + dx * i
            target_y = start_y + dy * i
            if is_on_board(target_x, target_y):
                target = get_piece(target_x, target_y)
                if target == "EM":
                    moves.append([(target_x, target_y), target])
                elif turn not in target:
                    moves.append([(target_x, target_y), target])
                    break
                else:
                    break
            else:
                break
    return moves


def stepper_check(start, piece):
    start_x, start_y = start
    moves = []
    knight_jumps = [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]
    king_steps = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, 1), (1, -1), (-1, -1)]
    directions = knight_jumps if "N" in piece else king_steps
    for dx, dy in directions:
        target_x = start_x + dx
        target_y = start_y + dy
        if is_on_board(target_x, target_y):
            target = get_piece(target_x, target_y)
            if target == "EM" or turn not in target:
                moves.append([(target_x, target_y), target])
    return moves


def get_moves_piece_type(start, piece):
    if piece[1] in "RBQ":
        return slide_ray(start, piece)
    elif piece[1] in "NK":
        return stepper_check(start, piece)
    else:
        return pawn_check(start, piece)


def pawn_check(start, piece):
    start_x, start_y = start
    moves = []
    direction = -1 if "w" in piece else 1
    fwd = (start_x, start_y + direction)
    start_row = 1 if direction == 1 else 6
    if is_on_board(*fwd) and get_piece(*fwd) == "EM":
        moves.append([fwd, "EM"])
        two_step = (start_x, start_y + 2 * direction)
        if is_on_board(*two_step) and get_piece(*two_step) == "EM" and start_y == start_row:
            moves.append([two_step, "EM"])
    for dx in [-1,1]:
        diag = (start_x + dx, start_y + direction)
        if is_on_board(*diag):
            target = get_piece(*diag)
            if target != "EM" and turn not in target:
                moves.append([diag, target])
    return moves


def is_on_board(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def get_pseudo_legal_moves():
    Move = namedtuple('Move',['start','target','moved','captured','special'])
    move_list = []
    for r in range(8):
        for c in range(8):
            crd = (c, r)
            p = get_piece(c, r)
            if turn not in p:
                continue
            for target, captured in get_moves_piece_type(crd, p):
                move_list.append(Move(crd, target, p, captured, "00"))
    return move_list

init()
while run:
    pseudo_moves = get_pseudo_legal_moves()
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected[0] is None:
                selected = select_piece(event.pos)
            else:
                selected = move(event.pos, selected, pseudo_moves)
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
