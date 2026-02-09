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
    ["ROOK",  "KNIGHT","BISHOP","QUEEN", "KING",  "BISHOP","KNIGHT","ROOK"],
    ["PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN"],
    ["EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY"],
    ["EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY"],
    ["EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY"],
    ["EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY"],
    ["PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN"],
    ["ROOK",  "KNIGHT","BISHOP","QUEEN", "KING",  "BISHOP","KNIGHT","ROOK"]
]
class Piece:
    def __init__(self,color,type):
        self.color = color
        self.type = type

def init():
    i = 0
    for yPos in range(8):
        for xPos in range(8):
            if i > 32:
                ct = "White"
            else:
                ct = "Black"
            if (xPos + yPos) % 2 != 0:
                color = "White"
            else:
                color = "Grey"
            if piecePos[yPos][xPos] != "EMPTY":
                occupied = [ct, piecePos[yPos][xPos]]
            else:
                occupied = []
            rect = pygame.Rect(50 + xPos * 50, 50 + yPos * 50, 50, 50)
            board.append([color, occupied, rect])
            i += 1
def selectpiece(pos):
    for x in board:
        if x[2].collidepoint(pos) and x[1] != [] and x[1][0] == turn:
            return x[2]
    return None


# def move(pos):
#     for x in board:
#         if x[2] == hlRect:
#             match x[1]:
#                case "ROOK":
#                    for y in piecePos:
#                        if index(x)%8 == index(y)%8


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
    for x in board:
        pygame.draw.rect(screen,x[0],x[2])
        if x[1]:
            screen.blit(pygame.transform.scale(pygame.image.load(f"Images\\pieces-basic-png\\{x[1][0]}-{x[1][1]}.png"),(50,50)), x[2])
    pygame.draw.rect(screen, "Black", pygame.Rect(50, 50, 400, 400), 2)
    if hlRect is not None:
        pygame.draw.rect(screen, "Red", hlRect, 1)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()