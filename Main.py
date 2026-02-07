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
    "ROOK",  "KNIGHT","BISHOP","QUEEN", "KING",  "BISHOP","KNIGHT","ROOK",
    "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",
    "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
    "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
    "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
    "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
    "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",  "PAWN",
    "ROOK",  "KNIGHT","BISHOP","QUEEN", "KING",  "BISHOP","KNIGHT","ROOK"
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
            if piecePos[i] != "EMPTY":
                occupied = [ct, piecePos[i]]
            else:
                occupied = []
            rect = pygame.Rect(50 + (xPos+1) * 50, 50 + (yPos+1) * 50, 50, 50)
            board.append([xPos + 1, yPos + 1, color, occupied, rect])
            i += 1
def selectPiece(pos):
    for x in board:
        if x[4].collidepoint(pos) and x[3] != [] and x[3][0] == turn:
            return x[4]
    return None


# def move(type):
#    match type:
#        case "ROOK":

init()
while run:
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            hlRect = selectPiece(event.pos)
    # wipe last screen
    screen.fill("white")
    # MAIN CODE
    for x in board:
        pygame.draw.rect(screen,x[2],x[4])
        if x[3]:
            screen.blit(pygame.transform.scale(pygame.image.load(f"Images\\pieces-basic-png\\{x[3][0]}-{x[3][1]}.png"),(50,50)),(50+x[0]*50,50+x[1]*50))
    pygame.draw.rect(screen, "Black", pygame.Rect(100, 100, 400, 400), 2)
    if hlRect != None:
        pygame.draw.rect(screen, "Red", hlRect, 1)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()
print(board)