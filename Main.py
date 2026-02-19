import pygame
import time
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
Move = namedtuple('Move', ['start', 'target', 'moved', 'captured', 'special'])
move_log = []
game_over = None
castle = {"w": [True, True], "b": [True, True]}


def init():
    for row in piecePos:
        for piece in row:
            if piece != "EM" and piece not in img:
                img[piece] = pygame.transform.scale(
                    pygame.image.load(f"Images\\pieces-basic-png\\{piece}.png"),
                                                    (50, 50)
                )
    for yPos in range(8):
        row = []
        for xPos in range(8):
            color = "White" if (xPos + yPos) % 2 == 0 else "Grey"
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            row.append([color, rect])
        board.append(row)
    legal_moves = get_legal_moves(piecePos, turn)
    return legal_moves


def select_piece(pos):
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            piece = get_piece(piecePos, col_idx, row_idx)
            if tile[1].collidepoint(pos) and piece != "EM" and turn in piece:
                return [tile[1], piece, (col_idx, row_idx)]
    return [None, "EM", ()]


def move(pos, start, legal_moves):
    target = None
    # Finds clicked tile coordinates and current occupation
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            if tile[1].collidepoint(pos):
                target = [tile[1], get_piece(piecePos, col_idx, row_idx), (col_idx, row_idx)]
                # If clicked tile contains another piece of current player, select that
                if turn in target[1]:
                    return target
    if target is None:
        return start
    # General Logic in Piece Movement:
    # 1. target tile is within move set of current piece
    # 2. there is no piece obstructing movement
    # 3. target tile is occupiable
    for m in legal_moves:
        if m.start == start[2] and m.target == target[2]:
            return capture(m)
    return start


def capture(move):
    global turn
    color = move.moved[0]
    pdir = 1 if "w" in move.moved else -1
    move_log.append(move)
    set_piece(piecePos, *move.target, move.moved)
    set_piece(piecePos, *move.start, "EM")
    # En Passant Flag
    if move.special == "EP":
        set_piece(piecePos, move.target[0], move.target[1] + pdir, "EM")
    # Castle Flag
    opp_row = 0 if color == "w" else 7
    if move.special == "CS":
        direction = (0, 3) if move.target[0] - move.start[0] > 0 else (7, 5)
        set_piece(piecePos, direction[0], move.start[1], "EM")
        set_piece(piecePos, direction[1], move.start[1], f"{color}R")
    for idx, corner in enumerate([0,7]):
        if move.target == (corner, opp_row):
            castle[("w" if color == "b" else "b")][idx] = False
    if "K" in move.moved:
        castle[color] = [False, False]
    # TODO: Promotion
    if "P" in move.moved:
        if (move.target[1] == 0 and "w" in move.moved) or \
           (move.target[1] == 7 and "b" in move.moved):
            set_piece(piecePos, *move.target, f"{color}Q")
    turn = "w" if turn == "b" else "b"
    return [None, "EM", ()]


def get_piece(board_state, x, y):
    return board_state[y][x]


def set_piece(board_state, x, y, piece):
    board_state[y][x] = piece


def get_slider_moves(board_state, start, piece):
    start_x, start_y = start
    moves = []
    directions = []
    opp = "b" if "w" in piece else "w"
    if piece[1] in "RQ":
        directions += [(-1, 0), (0, 1), (1, 0), (0, -1)]
    if piece[1] in "BQ":
        directions += [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for dx, dy in directions:
        for i in range(1, 8):
            target_crd = (start_x + dx * i, start_y + dy * i)
            if is_on_board(*target_crd):
                target = get_piece(board_state, *target_crd)
                if target == "EM":
                    moves.append(Move(start, target_crd, piece, target, "None"))
                elif opp in target:
                    moves.append(Move(start, target_crd, piece, target, "None"))
                    break
                else:
                    break
            else:
                break
    return moves


def get_stepper_moves(board_state, start, piece):
    start_x, start_y = start
    moves = []
    knight_jumps = [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]
    king_steps = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, 1), (1, -1), (-1, -1)]
    directions = knight_jumps if "N" in piece else king_steps
    opp = "b" if "w" in piece else "w"
    for dx, dy in directions:
        target_crd = (start_x + dx, start_y + dy)
        if is_on_board(*target_crd):
            target = get_piece(board_state, *target_crd)
            if target == "EM" or opp in target:
                moves.append(Move(start, target_crd, piece, target, "None"))
    return moves


def get_moves_piece_type(board_state, start, piece, last_move=None):
    if piece[1] in "RBQ":
        return get_slider_moves(board_state, start, piece)
    elif piece[1] in "NK":
        return get_stepper_moves(board_state, start, piece)
    else:
        return get_pawn_moves(board_state, start, piece, last_move)


def get_pawn_moves(board_state, start, piece, last_move=None):
    start_x, start_y = start
    moves = []
    direction = -1 if "w" in piece else 1
    fwd = start_y + direction
    start_row = 1 if direction == 1 else 6
    opp = "b" if "w" in piece else "w"
    if is_on_board(start_x, fwd) and get_piece(board_state, start_x, fwd) == "EM":
        moves.append(Move(start, (start_x, fwd), piece, get_piece(board_state, start_x, fwd), "None"))
        two_step = start_y + 2 * direction
        if (is_on_board(start_x, two_step)
                and get_piece(board_state, start_x, two_step) == "EM"
                and start_y == start_row):
            moves.append(Move(start, (start_x, two_step), piece, get_piece(board_state, start_x, two_step), "PJ"))
    for dx in [-1, 1]:
        diag = (start_x + dx, start_y + direction)
        if is_on_board(*diag):
            target = get_piece(board_state, *diag)
            if target != "EM" and opp in target:
                moves.append(Move(start, diag, piece, get_piece(board_state, *diag), "None"))
    # En Passant Check
    if last_move and last_move.special == "PJ":
        lm_x, lm_y = last_move.target
        if abs(lm_x - start_x) == 1 and start_y == lm_y:
            moves.append(Move(start, (lm_x, start_y + direction), piece, last_move.moved, "EP"))
    return moves


def is_on_board(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def get_pseudo_legal_moves(board_state, color, last_move=None):
    move_list = []
    for r in range(8):
        for c in range(8):
            crd = (c, r)
            p = get_piece(board_state, *crd)
            if color in p:
                move_list += get_moves_piece_type(board_state, crd, p, last_move)
                if p == f"{color}K":
                    move_list += get_castling_moves(board_state, color, crd, p)
    return move_list


def get_castling_moves(board_state, color, crd, piece):
    castle_moves = []
    opp = "w" if color == "b" else "b"
    checked_row = 0 if color == "b" else 7
    direction = [(2, range(1, 4), range(3, 5)), (6, range(5, 7), range(4, 7))]
    for idx, (target_x, empty_range, threat_range) in enumerate(direction):
        if castle[color][idx] and all(get_piece(board_state, i, checked_row) == "EM" for i in empty_range):
            threatened = False
            for i in threat_range:
                if attacked_check(board_state, opp, (i, checked_row)):
                    threatened = True
                    break
            if not threatened:
                castle_moves.append(Move(crd, (target_x, checked_row), piece, "EM", "CS"))
    return castle_moves


def get_king_pos(board_state, color):
    for r in range(8):
        for c in range(8):
            if get_piece(board_state, c, r) == f"{color}K":
                return c, r


def attacked_check(board_state, attack_color, crd):
    def_color = "w" if attack_color == "b" else "b"
    for s in get_slider_moves(board_state, crd, f"{def_color}Q"):
        attacker = get_piece(board_state, *s.target)
        dx = abs(crd[0] - s.target[0])
        dy = abs(crd[1] - s.target[1])
        if (dx == 0 or dy == 0) and attacker[1] in "RQ" and attack_color in attacker:
            return True
        elif dx == dy and attacker[1] in "BQ" and attack_color in attacker:
            return True
    for n in get_stepper_moves(board_state, crd, f"{def_color}N"):
        if get_piece(board_state, *n.target) == f"{attack_color}N":
            return True
    for k in get_stepper_moves(board_state, crd, f"{def_color}K"):
        if get_piece(board_state, *k.target) == f"{attack_color}K":
            return True
    step = 1 if attack_color == "w" else -1
    for dx in [-1, 1]:
        target = (crd[0] + dx, crd[1] + step)
        if is_on_board(*target):
            if get_piece(board_state, *target) == f"{attack_color}P":
                return True
    return False


def is_in_check(board_state, color):
    king_position = get_king_pos(board_state, color)
    if not king_position:
        return False
    attack_color = "w" if color == "b" else "b"
    return attacked_check(board_state, attack_color, king_position)


def get_legal_moves(board_state, color, last_move=None):
    legal_moves = []
    opp = "w" if color == "b" else "b"
    pdir = 1 if color == "w" else -1
    direction = (0, 0)
    for move in get_pseudo_legal_moves(board_state, color, last_move):
        set_piece(board_state, *move.start, "EM")
        save_target = get_piece(board_state, *move.target)
        set_piece(board_state, *move.target, move.moved)
        if move.special == "CS":
            direction = (0, 3) if move.target[0] - move.start[0] > 0 else (7, 5)
            set_piece(board_state, direction[0], move.start[1], "EM")
            set_piece(board_state, direction[1], move.start[1], f"{color}R")
        if move.special == "EP":
            set_piece(board_state, move.target[0], move.target[1] + pdir, "EM")
        if not is_in_check(board_state, color):
            legal_moves.append(move)
        if move.special == "EP":
            set_piece(board_state, move.target[0], move.target[1] + pdir, f"{opp}P")
        if move.special == "CS":
            set_piece(board_state, direction[1], move.start[1], "EM")
            set_piece(board_state, direction[0], move.start[1], f"{color}R")
        set_piece(board_state, *move.target, save_target)
        set_piece(board_state, *move.start, move.moved)
    return legal_moves


def check_final_states(board_state, color, legal_moves):
    if len(legal_moves) == 0:
        if is_in_check(board_state, color):
            return "Checkmate"
        else:
            return "Stalemate"
    return None


def undo_move():
    global turn
    move = move_log[-1]
    if move.special == "EP":
        opp = "w" if "b" in move.moved else "b"
        pdir = 1 if opp == "b" else -1
        set_piece(piecePos, move.target[0], move.target[1] + pdir, f"{opp}P")
    set_piece(piecePos, *move.target, move.captured)
    set_piece(piecePos, *move.start, move.moved)
    move_log.pop()
    turn = "w" if turn == "b" else "b"


legal_moves = init()
while run:
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected[0] is None:
                selected = select_piece(event.pos)
            else:
                ct = turn
                selected = move(event.pos, selected, legal_moves)
                if turn != ct:
                    last_m = move_log[-1] if move_log else None
                    legal_moves = get_legal_moves(piecePos, turn, last_m)
                    is_final = check_final_states(piecePos, turn, legal_moves)
                    if is_final is not None:
                        winner = "Black" if turn == "w" else "White"
                        if is_final == "Checkmate":
                            game_over = f"Checkmate! {winner} Player wins!"
                        else:
                            game_over = f"Draw! Stalemate!"
    # wipe last screen
    screen.fill("white")
    # FRONT END CODE
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            pygame.draw.rect(screen, *tile)
            piece = get_piece(piecePos, col_idx, row_idx)
            if piece != "EM":
                screen.blit(img[piece], tile[1])
    pygame.draw.rect(screen, "Black", pygame.Rect(50, 50, 400, 400), 2)
    if selected[0] is not None:
        pygame.draw.rect(screen, "Red", selected[0], 1)
    pygame.display.flip()

    if game_over:
        print(game_over)
        time.sleep(3)
        run = False

    dt = clock.tick(60) / 1000

pygame.quit()
