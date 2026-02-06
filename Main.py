import pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
# delta time (s) since last frame; useful for frame-independent physics
dt = 0
# current tile color
aMap = ["a","b","c","d","e","f","g","h"]
board = []
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
            ct = i <= 31
            if (xPos + yPos) % 2 != 0:
                color = "White"
            else:
                color = "Black"
            if piecePos[i] != "EMPTY":
                occupied = [ct, piecePos[i]]
            else:
                occupied = []
            board.append([xPos + 1 , yPos + 1, color, occupied])
            i += 1
#def selectPiece():


#def move(type):
#    match type:
#        case "ROOK":

init()
while run:
    # poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    # wipe last screen
    screen.fill("white")
    # MAIN CODE
    for x in board:
        pygame.draw.rect(screen,x[2],pygame.Rect(50+x[0]*50,50+x[1]*50,50,50))
        #match x[3]:
        #    case "EMPTY":

    pygame.draw.rect(screen, "Black", pygame.Rect(100, 100, 400, 400), 2)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()
print(board)