import pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
run = True
#delta time (s) since last frame; useful for frame-independent physics
dt = 0
#current tile color
bcolor = "undefined"
aMap = ["a","b","c","d","e","f","g","h"]
occupied = []
board = []
#check if current piece is white
colorToggle = True
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
class piece:
    def __init__(self,color,type):
        self.color = color
        self.type = type

while run:
    #poll for events (actions done)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    #wipe last screen
    screen.fill("white")
    #MAIN CODE
    i = 0
    board = []
    for y in range(8):
        for x in range(8):
            colorToggle = i <= 31
            if (x+y)%2 != 0:
                bcolor = "White"
            else:
                bcolor = "Black"
            if piecePos[i] != "EMPTY":
                occupied = [colorToggle, piecePos[i]]
            else:
                occupied = []
            board.append([aMap[x], y+1, bcolor, occupied])
            i += 1
            pygame.draw.rect(screen,bcolor,pygame.Rect((150+x*50),(650-y*50),50,50))
    pygame.draw.rect(screen, "Black", pygame.Rect(150, 300, 400, 400), 2)
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()
print(board)