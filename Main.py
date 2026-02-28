import pygame
from collections import namedtuple

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
# delta time (s) since last frame; useful for frame-independent physics
dt = 0
font = pygame.font.SysFont("Times New Roman", 15, bold=True)
img = {}
board = []
selected = [None, "EM", ()]
Move = namedtuple('Move', ['start', 'target', 'moved', 'captured', 'special', 'old_castle', 'old_stale'])
# Promotion UI Stuff
overlay = pygame.Surface((400, 400))
overlay.set_alpha(160)
overlay.fill((20, 20, 20))
pro_menu_pos = (0, 0)
pro_rects = []
# Evaluation stuff
piece_values = {"P": 100, "Q": 1000, "K": 10000, "B": 300, "N": 300, "R": 500}


# TODO: Wrap globals into something to keep it unique to each user (class?)
class GameState:
    def __init__(self):
        self.board_state = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.turn = "w"
        self.move_log = []
        self.castle = {"w": [True, True], "b": [True, True]}
        self.game_over = None
        self.is_promo = False
        # Tracks the 50-Turn-Stalemate rule
        self.stale_count = 0
        self.legal_moves = []
        self.pending_move = None

    def set_piece(self, x, y, piece):
        self.board_state[y][x] = piece

    def get_piece(self, x, y):
        return self.board_state[y][x]

    # move check for rooks, bishops, queens; sends rays to directions to fill the move list
    def get_slider_moves(self, start, piece):
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
                    target = self.get_piece(*target_crd)
                    if target == "EM":
                        moves.append(Move(
                            start,
                            target_crd,
                            piece,
                            target,
                            "None",
                            {k: v[:] for k, v in self.castle.items()},
                            self.stale_count
                        ))
                    elif opp in target:
                        moves.append(Move(
                            start,
                            target_crd,
                            piece,
                            target,
                            "None",
                            {k: v[:] for k, v in self.castle.items()},
                            self.stale_count))
                        break
                    else:
                        break
                else:
                    break
        return moves

    # move check for kings and knights; iterating through potential positions
    def get_stepper_moves(self, start, piece):
        start_x, start_y = start
        moves = []
        knight_jumps = [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]
        king_steps = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, 1), (1, -1), (-1, -1)]
        directions = knight_jumps if "N" in piece else king_steps
        opp = "b" if "w" in piece else "w"
        for dx, dy in directions:
            target_crd = (start_x + dx, start_y + dy)
            if is_on_board(*target_crd):
                target = self.get_piece(*target_crd)
                if target == "EM" or opp in target:
                    moves.append(Move(
                        start,
                        target_crd,
                        piece,
                        target,
                        "None",
                        {k: v[:] for k, v in self.castle.items()},
                        self.stale_count
                    ))
        return moves

    # Move check for pawns;
    def get_pawn_moves(self, start, piece, last_move=None):
        start_x, start_y = start
        moves = []
        direction = -1 if "w" in piece else 1
        fwd = start_y + direction
        start_row = 1 if direction == 1 else 6
        opp = "b" if "w" in piece else "w"
        if is_on_board(start_x, fwd) and self.get_piece(start_x, fwd) == "EM":
            if fwd in [0, 7]:
                moves.append(Move(
                    start,
                    (start_x, fwd),
                    piece,
                    self.get_piece(start_x, fwd),
                    "PR",
                    {k: v[:] for k, v in self.castle.items()},
                    self.stale_count
                ))
            else:
                moves.append(Move(
                    start,
                    (start_x, fwd),
                    piece,
                    self.get_piece(start_x, fwd),
                    "None",
                    {k: v[:] for k, v in self.castle.items()},
                    self.stale_count
                ))
            two_step = start_y + 2 * direction
            if (is_on_board(start_x, two_step)
                    and self.get_piece(start_x, two_step) == "EM"
                    and start_y == start_row):
                moves.append(Move(
                    start,
                    (start_x, two_step),
                    piece,
                    self.get_piece(start_x, two_step),
                    "PJ",
                    {k: v[:] for k, v in self.castle.items()},
                    self.stale_count
                ))
        for dx in [-1, 1]:
            diag = (start_x + dx, start_y + direction)
            if is_on_board(*diag):
                target = self.get_piece(*diag)
                if target != "EM" and opp in target:
                    if diag[1] in [0, 7]:
                        moves.append(Move(
                            start,
                            diag,
                            piece,
                            self.get_piece(*diag),
                            "PR",
                            {k: v[:] for k, v in self.castle.items()},
                            self.stale_count
                        ))
                    else:
                        moves.append(Move(
                            start,
                            diag,
                            piece,
                            self.get_piece(*diag),
                            "None",
                            {k: v[:] for k, v in self.castle.items()},
                            self.stale_count
                        ))
        # En Passant Check: enable capture if enemy pawn jumps past your own
        if last_move and last_move.special == "PJ":
            lm_x, lm_y = last_move.target
            if abs(lm_x - start_x) == 1 and start_y == lm_y:
                moves.append(Move(
                    start,
                    (lm_x, start_y + direction),
                    piece,
                    last_move.moved,
                    "EP",
                    {k: v[:] for k, v in self.castle.items()},
                    self.stale_count
                ))
        return moves

    # Wrapper to assign piece to respective move function
    def get_moves_piece_type(self, start, piece, last_move=None):
        if piece[1] in "RBQ":
            return self.get_slider_moves(start, piece)
        elif piece[1] in "NK":
            return self.get_stepper_moves(start, piece)
        else:
            return self.get_pawn_moves(start, piece, last_move)

    # checks threats on specific tile; simulates enemy piece to access respective
    # move functions for a reverse check
    def attacked_check(self, attack_color, crd):
        def_color = "w" if attack_color == "b" else "b"
        for s in self.get_slider_moves(crd, f"{def_color}Q"):
            attacker = self.get_piece(*s.target)
            dx = abs(crd[0] - s.target[0])
            dy = abs(crd[1] - s.target[1])
            if (dx == 0 or dy == 0) and attacker[1] in "RQ" and attack_color in attacker:
                return True
            elif dx == dy and attacker[1] in "BQ" and attack_color in attacker:
                return True
        for n in self.get_stepper_moves(crd, f"{def_color}N"):
            if self.get_piece(*n.target) == f"{attack_color}N":
                return True
        for k in self.get_stepper_moves(crd, f"{def_color}K"):
            if self.get_piece(*k.target) == f"{attack_color}K":
                return True
        step = 1 if attack_color == "w" else -1
        for dx in [-1, 1]:
            target = (crd[0] + dx, crd[1] + step)
            if is_on_board(*target):
                if self.get_piece(*target) == f"{attack_color}P":
                    return True
        return False

    # Castling check; are pieces unobstructed, is King not threatened during the move
    def get_castling_moves(self, crd, piece, color=None):
        if color is None:
            color = self.turn
        castle_moves = []
        opp = "w" if color == "b" else "b"
        checked_row = 0 if color == "b" else 7
        direction = [(2, range(1, 4), range(3, 5)), (6, range(5, 7), range(4, 7))]
        for idx, (target_x, empty_range, threat_range) in enumerate(direction):
            if self.castle[color][idx] and all(self.get_piece(i, checked_row) == "EM" for i in empty_range):
                threatened = False
                for i in threat_range:
                    if self.attacked_check(opp, (i, checked_row)):
                        threatened = True
                        break
                if not threatened:
                    castle_moves.append(Move(
                        crd,
                        (target_x, checked_row),
                        piece,
                        "EM",
                        "CS",
                        {k: v[:] for k, v in self.castle.items()},
                        self.stale_count
                    ))
        return castle_moves

    # first check on every move possible, disregarding king checks
    def get_pseudo_legal_moves(self, color=None, last_move=None):
        if color is None:
            color = self.turn
        move_list = []
        for r in range(8):
            for c in range(8):
                crd = (c, r)
                p = self.get_piece(*crd)
                if color in p:
                    move_list += self.get_moves_piece_type(crd, p, last_move)
                    if p == f"{color}K":
                        move_list += self.get_castling_moves(crd, p, color)
        return move_list

    def get_king_pos(self, color=None):
        if color is None:
            color = self.turn
        for r in range(8):
            for c in range(8):
                if self.get_piece(c, r) == f"{color}K":
                    return c, r

    def is_in_check(self, color=None):
        if color is None:
            color = self.turn
        king_position = self.get_king_pos(color)
        if not king_position:
            return False
        attack_color = "w" if color == "b" else "b"
        return self.attacked_check(attack_color, king_position)

    def check_final_states(self, legal_moves, color=None):
        if color is None:
            color = self.turn
        if len(legal_moves) == 0:
            if self.is_in_check(color):
                return "Checkmate"
            else:
                return "Stalemate"
        # 50-Move-Rule includes 50 white and 50 black moves, hence 100
        elif self.stale_count == 100:
            return "Stalemate"
        return None

    # updates legal moves and checks for end states
    def resolve_turn(self):
        last_m = self.move_log[-1] if self.move_log else None
        self.legal_moves = self.get_legal_moves(self.turn, last_m)
        is_final = self.check_final_states(self.legal_moves, self.turn)
        if is_final is not None:
            winner = "Black" if self.turn == "w" else "White"
            if is_final == "Checkmate":
                self.game_over = font.render(f"Checkmate! {winner} Player wins!", True, (0, 0, 0))
            else:
                self.game_over = font.render("Draw! Stalemate!", True, (0, 0, 0))

    # simulates piece movement
    def make_move(self, move):
        self.set_piece(*move.target, move.moved)
        self.set_piece(*move.start, "EM")
        color = move.moved[0]
        # En Passant Flag
        if move.special == "EP":
            pdir = 1 if "w" in move.moved else -1
            self.set_piece(move.target[0], move.target[1] + pdir, "EM")
        # Castle Flag
        if move.special == "CS":
            direction = (0, 3) if move.target[0] - move.start[0] < 0 else (7, 5)
            self.set_piece(direction[0], move.start[1], "EM")
            self.set_piece(direction[1], move.start[1], f"{color}R")
        if "K" in move.moved:
            self.castle[color] = [False, False]
        for side, row in [("w", 7), ("b", 0)]:
            for i, col in enumerate([0, 7]):
                if move.start == (col, row) or move.target == (col, row):
                    self.castle[side][i] = False
        if move.moved[1] == "P" or move.captured != "EM":
            self.stale_count = 0
        else:
            self.stale_count += 1
        self.move_log.append(move)
        self.turn = "w" if self.turn == "b" else "b"
        return [None, "EM", ()]

    # reads the latest move and reverses its effects
    def undo_move(self):
        # No undo to do if no move has been done
        if len(self.move_log) == 0:
            return
        move = self.move_log.pop()
        # Put the rook back if castling
        if move.special == "CS":
            color = move.moved[0]
            direction = (0, 3) if move.target[0] - move.start[0] < 0 else (7, 5)
            self.set_piece(direction[0], move.start[1], f"{color}R")
            self.set_piece(direction[1], move.start[1], "EM")
        # Put the pawn back if En Passant
        if move.special == "EP":
            opp = "w" if "b" in move.moved else "b"
            pdir = 1 if opp == "b" else -1
            self.set_piece(move.target[0], move.target[1] + pdir, f"{opp}P")
            self.set_piece(*move.target, "EM")
        else:
            self.set_piece(*move.target, move.captured)
        # Reverse Promotion
        if move.special == "PR":
            self.set_piece(*move.start, f"{move.moved[0]}P")
        else:
            self.set_piece(*move.start, move.moved)
        # Restore old game state
        self.castle = move.old_castle
        self.stale_count = move.old_stale
        self.turn = "w" if self.turn == "b" else "b"
        self.game_over = None
        self.is_promo = False
        return [None, "EM", ()]

    # simulates every pseudo-legal move for king check
    def get_legal_moves(self, color=None, last_move=None):
        if color is None:
            color = self.turn
        legal_moves = []
        for move in self.get_pseudo_legal_moves(color, last_move):
            self.make_move(move)
            if not self.is_in_check(color):
                legal_moves.append(move)
            self.undo_move()
        return legal_moves

    def evaluate_board(self):
        score = 0
        for row in self.board_state:
            for piece in row:
                if piece != "EM":
                    value = piece_values[piece[1]]
                    if piece[0] == "w":
                        score += value
                    else:
                        score -= value
        return score

    def restart(self):
        self.is_promo = False
        self.board_state[:] = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["EM", "EM", "EM", "EM", "EM", "EM", "EM", "EM"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_log.clear()
        self.stale_count = 0
        self.turn = "w"
        self.game_over = None
        self.resolve_turn()
        return [None, "EM", ()]


# load the images and prepare to draw the board
def init(gs):
    for row in gs.board_state:
        for piece in row:
            if piece != "EM" and piece not in img:
                img[piece] = pygame.transform.scale(
                    pygame.image.load(f"Images\\pieces-basic-png\\{piece}.png"),
                    (50, 50)
                )
    img["Undo"] = pygame.transform.scale(
        pygame.image.load("Images\\undo.png"), (50, 50)
    )
    img["Restart"] = pygame.transform.scale(
        pygame.image.load("Images\\restart.png"), (50, 50)
    )
    for yPos in range(8):
        row = []
        for xPos in range(8):
            color = "White" if (xPos + yPos) % 2 == 0 else "Grey"
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            row.append([color, rect])
        board.append(row)


# returns the tile at mouse click, if possible
def select_piece(pos, gs):
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            piece = gs.get_piece(col_idx, row_idx)
            if tile[1].collidepoint(pos) and piece != "EM" and gs.turn in piece:
                return [tile[1], piece, (col_idx, row_idx)]
    return [None, "EM", ()]


# Wrapper to determine target at mouse click and check if selected piece can move there
def move(pos, start, gs):
    global pro_menu_pos
    target = None
    # Finds clicked tile coordinates and current occupation
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            if tile[1].collidepoint(pos):
                target = [tile[1], gs.get_piece(col_idx, row_idx), (col_idx, row_idx)]
                # If clicked tile contains another piece of current player, select that
                if gs.turn in target[1]:
                    return target
    if target is None:
        return start
    # General Logic in Piece Movement:
    # 1. target tile is within move set of current piece
    # 2. there is no piece obstructing movement
    # 3. target tile is occupiable
    for m in gs.legal_moves:
        if m.start == start[2] and m.target == target[2]:
            if m.special == "PR":
                gs.pending_move = m
                gs.is_promo = True
                pro_menu_pos = pygame.mouse.get_pos()
                return [None, "EM", ()]
            else:
                return gs.make_move(m)
    return start


def is_on_board(x, y):
    return 0 <= x < 8 and 0 <= y < 8


# draws the Promotion Selection UI
def draw_promo_select():
    mouse_x, mouse_y = pro_menu_pos
    pro_rects.clear()
    screen.blit(overlay, (50, 50))
    color = gs.pending_move.moved[0]
    pro_options = [f"{color}Q", f"{color}R", f"{color}N", f"{color}B"]
    for i, option in enumerate(pro_options):
        rect = pygame.Rect(mouse_x, mouse_y + i * 50, 50, 50)
        pro_rects.append(rect)
        pygame.draw.rect(screen, "White", rect)
        pygame.draw.rect(screen, "Black", rect, 2)
        screen.blit(img[option], rect)


def promo_click(mouse_pos):
    color = gs.pending_move.moved[0]
    pro_options = [f"{color}Q", f"{color}R", f"{color}N", f"{color}B"]
    for i, rect in enumerate(pro_rects):
        if rect.collidepoint(mouse_pos):
            return pro_options[i]
    return None


# def greed(board_state, legal_moves):
#     for move in legal_moves:


# Main loop
gs = GameState()
gs.resolve_turn()
init(gs)
while run:
    # wipe last screen
    screen.fill("white")
    # draws the current board state
    for row_idx, row_data in enumerate(board):
        for col_idx, tile in enumerate(row_data):
            pygame.draw.rect(screen, *tile)
            piece = gs.get_piece(col_idx, row_idx)
            if piece != "EM":
                screen.blit(img[piece], tile[1])
    pygame.draw.rect(screen, "Black", pygame.Rect(50, 50, 400, 400), 2)
    if selected[0] is not None:
        pygame.draw.rect(screen, "Red", selected[0], 1)
    if gs.is_promo:
        draw_promo_select()
    # TODO: End screen
    if gs.game_over:
        screen.blit(overlay, (50, 50))
        pygame.draw.rect(screen, "White", pygame.Rect(100, 100, 300, 150))
        pygame.draw.rect(screen, "Black", pygame.Rect(100, 100, 300, 150), 1)
        screen.blit(gs.game_over, (150, 125))
    screen.blit(img["Undo"], pygame.Rect(450, 400, 50, 50))
    screen.blit(img["Restart"], pygame.Rect(450, 350, 50, 50))
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(450, 400, 50, 50).collidepoint(event.pos):
            selected = gs.undo_move()
            gs.resolve_turn()
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(450, 350, 50, 50).collidepoint(event.pos):
            selected = gs.restart()
            break
        if not gs.game_over:
            if gs.is_promo:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pro_selected = promo_click(pygame.mouse.get_pos())
                    if pro_selected:
                        new_move = Move(
                            gs.pending_move.start,
                            gs.pending_move.target,
                            pro_selected,
                            gs.pending_move.captured,
                            "PR",
                            {k: v[:] for k, v in gs.castle.items()},
                            gs.stale_count
                        )
                        gs.make_move(new_move)
                        gs.resolve_turn()
                        gs.is_promo = False
                        pro_rects = []
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if selected[0] is None:
                    selected = select_piece(event.pos, gs)
                else:
                    ct = gs.turn
                    selected = move(event.pos, selected, gs)
                    # only updates legal moves and game end after an actual move was made
                    if gs.turn != ct:
                        gs.resolve_turn()
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
