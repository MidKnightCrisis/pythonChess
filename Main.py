import pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
# delta time (s) since last frame; useful for frame-independent physics
dt = 0
# current tile color
# aMap = ["a","b","c","d","e","f","g","h"]
turn = "White"
board = []
hlRect = None
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
class Piece:
    def __init__(self,color,type):
        self.color = color
        self.type = type

def init():
    for yPos in range(8):
        row = []
        for xPos in range(8):
            color = "White" if (xPos + yPos) % 2 == 0 else "Grey"
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            row.append([color, rect])
        board.append(row)
def selectpiece(pos):
    for row in board:
        row_index = board.index(row)
        for tile in row:
            tile_index = row.index(tile)
            currentPos = piecePos[row_index][tile_index]
            if tile[1].collidepoint(pos) and currentPos != "EM" and "w" in currentPos:
                return tile[1]
    return None


# def move(pos):
#     for x in board:
#         if x[2] == hlRect:
#             match x[1]:
#                case "ROOK":
#                    for y in piecePos:
#                        if board.index(x) == index(y)


init()
while run:
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            hlRect = selectpiece(event.pos)
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
    if hlRect is not None:
        pygame.draw.rect(screen, "Red", hlRect, 1)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()