import pygame, sys
import TicTacToeLib.TicTacToeLib as TTTL
from random import choice
BG = "res/paper.png"
CD = "res/choosedialog.png"
PA = "res/playagain.png"
XB = "res/xboxbutton.png"
OB = "res/oboxbutton.png"
XPC = "res/X96.png"
OPC = "res/O96.png"
BOARD = "res/board.png"
YES = "res/yesbutton.png"
NO = "res/nobutton.png"

STATE_CHOOSE = 0
STATE_PLAY = 1
STATE_GAME_OVER = 2



# Sprite for Yes/No buttons on Play Again? "dialog"
class YNButton(pygame.sprite.Sprite):
    def __init__(self, img, x, y, yes = True):
        super(YNButton, self).__init__()
        self.yes = yes
        temp_image = pygame.image.load(img)
        self.size = (self.width, self.height) = (60,30)
        self.image = pygame.transform.smoothscale(temp_image, self.size)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
# Sprite for X/O buttons on Choose Piece "dialog"
class BoxButton(pygame.sprite.Sprite):
    def __init__(self, img, name, x, y):
        super(BoxButton, self).__init__()
        self.name = name
        temp_image = pygame.image.load(img)
        self.size = (self.width, self.height) = (66,66)
        self.image = pygame.transform.smoothscale(temp_image, self.size)
        self.rect = pygame.Rect(x, y, self.width, self.height)

# Sprite for X/O pieces        
class Piece(pygame.sprite.Sprite):
    def __init__(self, piece, x, y):
        super(Piece, self).__init__()
        img = XPC if piece == TTTL.PIECE_X else OPC
        temp_image = pygame.image.load(img)
        self.size = (self.width, self.height) = (96,96)
        self.image = pygame.transform.smoothscale(temp_image, self.size)
        self.rect = pygame.Rect(x, y, self.width, self.height)

# Sprite class for game board that also stores the logical TTTL.Board         
class GameBoard(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(GameBoard, self).__init__()
        temp_image = pygame.image.load(BOARD)
        self.size = (self.width, self.height) = (288,288)
        self.cell_size = (self.cell_width, self.cell_height) = (96,96)
        self.image = pygame.transform.smoothscale(temp_image, self.size)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.cell_list = self.createCellList()
        self.board = None
        
        self.pieces = pygame.sprite.Group()
    
    # create a map for position to cell    
    def createCellList(self):
        cells = []
        x,y = 0,0
        for i in xrange(9):
            cells.append(pygame.Rect(x,y,96,96))
            # new row
            if (i+1) % 3 == 0:
                x = 0
                y += self.cell_height
            else:
                x += self.cell_width
                
        return cells            
    
    # calculate the relative position in the board's rect    
    def __getRelativePos(self, pos):
        absolute_x, absolute_y = pos
        relative_x = absolute_x - self.rect.left
        relative_y = absolute_y - self.rect.top
        return (relative_x, relative_y)
    
    # determine which cell corresponds to the current position
    def whichCell(self, pos):
        relative_pos = self.__getRelativePos(pos)
        for idx, cell in enumerate(self.cell_list):
            if cell.collidepoint(relative_pos):
                return idx
        
        # this should never get called, but just in case    
        return TTTL.NO_MOVE
            
    # have AI calculate and make it's move        
    def moveAI(self, aiplayer):
        idx = aiplayer.move(self.board)
        self.movePlayer(aiplayer, idx)
        
    # general pupose method for placing a piece on the Board then GameBoard
    def movePlayer(self, player, idx):
        if idx != TTTL.NO_MOVE:
            if self.board.move(player, idx):
                self.move(idx)
                return True
        
        return False
 
    # add a sprite representing the piece to the GameBoard
    def move(self, idx):
        if idx in xrange(9):
            piece = self.board.getGameBoard()[idx]
            if piece != TTTL.BLANK:
                x = self.cell_list[idx].left + self.rect.left
                y = self.cell_list[idx].top + self.rect.top
                self.pieces.add(Piece(piece,x,y))
        
    # check to see if any of the game ending conditions have been met        
    def isGameOver(self, player1, player2):
        return ( self.board.isBoardFull() or 
                self.board.isWinner(player1) or 
                self.board.isWinner(player2) )
        
    # Winner is X, O, or Draw?
    def getWinner(self, player1, player2):
        piece = TTTL.BLANK
        if self.board.isWinner(player1):
            piece = player1.piece
        elif self.board.isWinner(player2):
            piece = player2.piece
        return piece
                                

# main game class that includes the game loop and event handling
class Main(object):
    def __init__(self):
        self.setup()
        
    # reusable setup method convenient for repeating play
    def setup(self):
        pygame.init()
        self.game_over = False
        size = (self.width, self.height) = (640,480)
        self.screen = pygame.display.set_mode(size)
        self.black = (0, 0, 0)
        self.background_image = pygame.image.load(BG)
        self.choose_dialog = pygame.image.load(CD)
        self.playagain = pygame.image.load(PA)
        self.game_board = GameBoard(self.width/2-144,self.height/2-144)
        self.boardGroup = pygame.sprite.GroupSingle(self.game_board)
        self.game_state = STATE_CHOOSE
        self.clicked = False
        self.click_pos = (0,0)
        self.player = None
        self.aiplayer = None
        self.aipiece = None
        self.turn = None
        self.moved = False
        self.winner = None
        self.box_buttons = pygame.sprite.Group()
        self.box_buttons.add(BoxButton(XB, TTTL.PIECE_X, 255, 179))
        self.box_buttons.add(BoxButton(OB, TTTL.PIECE_O, 339,179))
        
        self.play_x = self.width/2-70
        self.play_y = self.height-70
        self.yn_buttons = pygame.sprite.Group()
        self.yn_buttons.add(YNButton(YES, self.play_x+5, self.play_y+30-5));
        self.yn_buttons.add(YNButton(NO, self.play_x+140-60-5, self.play_y+30-5, False))
        
        self.setup_background()
    
    def setup_background(self):
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.screen.blit(self.background_image, (0, 0))
        pygame.display.flip()
    
    # main drawing method    
    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        if self.game_state == STATE_CHOOSE:
            self.screen.blit(self.choose_dialog, (250, 150))
            self.box_buttons.update()
            self.box_buttons.draw(self.screen)
        
        # we want to keep drawing the game board even after the game ends
        if self.game_state == STATE_PLAY or self.game_state == STATE_GAME_OVER:
            self.boardGroup.update()
            self.boardGroup.draw(self.screen)
            self.game_board.pieces.update()
            self.game_board.pieces.draw(self.screen)
            
            # Additional things to add for game over:
            # show the winner as well as show the play again? question and buttons
            if self.game_state == STATE_GAME_OVER:
                winner_text = ""
                if self.winner == TTTL.BLANK:
                    winner_text =  "Draw"
                elif self.winner == self.aipiece:
                    winner_text = "CPU Wins!"
                else:
                    winner_text = "Human Wins! Inconceivable!!!!"
                
                # print winner_text
                if pygame.font:
                    font = pygame.font.Font(None, 36)
                    text = font.render(winner_text, 1, (10, 10, 10))
                    textpos = text.get_rect(centerx=self.screen.get_width()/2)
                    self.screen.blit(text, textpos)
                
                self.screen.blit(self.playagain,(self.play_x,self.play_y))
                self.yn_buttons.update()
                self.yn_buttons.draw(self.screen)
            
            
        pygame.display.flip()
    
    # determine which piece has the next turn
    def nextTurn(self):
        return TTTL.PIECE_X if self.turn == TTTL.PIECE_O else TTTL.PIECE_O
    
    # a wrapper around AI movement    
    def moveAI(self):
        # if it is AI turn and a move hasn't been made
        if self.turn == self.aipiece and not self.moved:
            self.game_board.moveAI(self.aiplayer)
            self.moved = True
            self.turn = self.nextTurn()
    
    # monolithic method to route a "click"    
    def processClick(self, state):
        # At the start of the game we need to choose a piece 
        if state == STATE_CHOOSE:
            # look through our list of buttons
            for button in self.box_buttons.sprites():
                # see if our click collides with a button
                if button.rect.collidepoint(self.click_pos):
                    # player gets the piece clicked
                    self.player = TTTL.Player(button.name)
                    
                    # AI gets the opposite piece
                    self.aipiece = TTTL.PIECE_X if button.name == TTTL.PIECE_O else TTTL.PIECE_O
                    self.aiplayer = TTTL.AIPlayer(self.aipiece)
                    
                    # setup the logical board now that we are ready
                    self.game_board.board = TTTL.Board()
                    
                    # randomly determine who goes first
                    self.turn = choice([TTTL.PIECE_X,TTTL.PIECE_O])
                    
                    # move to a ready state
                    self.game_state = STATE_PLAY
                    
                    # now that we have the correct button leave
                    return

        # Handle human player movement
        if state == STATE_PLAY and self.turn != self.aipiece:
            # check to see if our click collides with the GameBoard
            if self.game_board.rect.collidepoint(self.click_pos):
                # get the cell number from the position of the click
                idx = self.game_board.whichCell(self.click_pos)
                # handle player movement
                if self.game_board.movePlayer(self.player, idx):
                    self.turn = self.nextTurn()
                    self.moved = True
        
        # game over - handle play again? yes/no        
        if state == STATE_GAME_OVER:
            for button in self.yn_buttons.sprites():
                if button.rect.collidepoint(self.click_pos):
                    self.game_over = not button.yes
                    
                    # if the user chose to play again reset everything
                    if not self.game_over:
                        self.setup()


    def event_loop(self):
        while not self.game_over:
            # handle relevant input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # basic click logic - record position where button goes down    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.clicked = True
                    self.click_pos = pygame.mouse.get_pos()
                # finish click
                if event.type == pygame.MOUSEBUTTONUP and self.clicked:
                    self.clicked = False
                    self.processClick(self.game_state)
            
            # moveAI if need be           
            if self.game_state == STATE_PLAY:
                self.moveAI()
            
            if self.moved:
                #check for end of game
                if self.game_board.isGameOver(self.player, self.aiplayer):
                    self.winner = self.game_board.getWinner(self.player,self.aiplayer)
                    self.game_state = STATE_GAME_OVER
                    
                self.moved = False

#                
            self.draw()
            pygame.time.delay(30)


if __name__ == '__main__':
    app = Main()
    app.event_loop()