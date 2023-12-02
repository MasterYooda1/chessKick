import pygame
import pygame_gui
import sqlite3
import chess
import math

square_indexes = []
for i in range(64):
    square_indexes.append(i)
    print(square_indexes[i])

col_names = ["a", "b", "c", "d", "e", "f", "g", "h"]
col_nums = [0, 1, 2, 3, 4, 5, 6, 7]
opening_id = 1
incorrect_pieces = []
# Code which is used to create a piece.
class Piece:
    piece_id = 0
    def __init__(self, x, y, image_path, letter, colour):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.letter = letter
        self.original_pos = (x, y)
        #self.last_pos = (x, y)
        self.colour = colour
        self.row = (1000 - y) // 100 
        self.col = x // 100 
        self.square = f"{col_names[self.col]}{self.row}"
        self.dead = False

        Piece.piece_id += 1
        self.id = Piece.piece_id

pygame.init()
board = chess.Board()

COLOUR1 = (75,115,153)
COLOUR2 = (234,233,210)

temp_font = pygame.font.SysFont(None, 20)


# Database Connections
db_connection = sqlite3.connect('chessKick.db')
db_cursor = db_connection.cursor()

# Window Info
pygame.display.set_caption('ChessKick')
window_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, display=0)#, vsync=True,
icon_surface = pygame.image.load("assets/icons/chessKickLogo60x60.png")
pygame.display.set_icon(icon_surface)

x, y = window_surface.get_size()
# Background Size and Colour
background = pygame.Surface((x, y))
background.fill(pygame.Color('#27374d'))

# UI Manager
manager = pygame_gui.UIManager((x, y), 'themes.json')


# A Function which adds moves into a text box
#def update_text_box():
    
    #for move in board.move_stack:
        #print(len(move))
        #san_move = board.san(move)
        #move_string.append(san_move)
    #moves_box.html_text = "<br>".join(move_string)
    #print(move_string)

# A Function which updates the boards pieces for captures and moves
def update_board():
    for i, square in enumerate(chess.SQUARES):
        if board.piece_at(square) is not None:
            px = chess.square_file(square) * 100 + 75
            py = 800 - chess.square_rank(square) * 100 + 50
            for piece in pieces:
                if piece.letter == str(board.piece_at(square)) and piece.piece_id == board.piece_at(square).piece_id:
                    piece.rect.x = px
                    piece.rect.y = py
                    piece.square = square
    print(board)

# ------------------ Items Here ---------------------
top_panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), (x, 75)),
                                         manager=manager,
                                         object_id="#Top_Panel")

# Help Image and Button
help_surface = pygame.image.load('assets/icons/help-icon-48.png')
help_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x-156, 10), (48, 48)),
                                                manager=manager,
                                                text='',
                                                container=top_panel,
                                                object_id="#Help_Button")
help_icon = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((x-156, 10), (48, 48)), image_surface=help_surface, container=top_panel)

#Settings Image and Button
settings_surface = pygame.image.load('assets/icons/settings-icon-48.png')
settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x-108, 10), (48, 48)),
                                                manager=manager,
                                                text='',
                                                container=top_panel,
                                                object_id="#Settings_Button")
settings_icon = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((x-108, 10), (48, 48)), image_surface=settings_surface, container=top_panel)

#Home Button and Image
home_surface = pygame.image.load('assets/icons/home-icon-48.png')
home_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x-60, 10), (48, 48)),
                                                manager=manager,
                                                text='',
                                                container=top_panel,
                                                object_id="#Help_Button")
home_icon = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((x-60, 10), (48, 48)), image_surface=home_surface, container=top_panel)

# Other UI Elements
main_label = pygame_gui.elements.UILabel(manager=manager, relative_rect=pygame.Rect((17,17),(400,40)), text="Practice your Opening Moves", object_id='#main_labelso')

menu_panel = pygame_gui.elements.UIPanel(manager=manager, relative_rect=pygame.Rect((0, 75), (x, y-75 )), element_id="@Bottom_Panel")

board_panel = pygame_gui.elements.UIPanel(manager=manager, relative_rect=pygame.Rect((75, 75), (800, 800)), container=menu_panel, element_id="#Top_Panel")

moves_box = pygame_gui.elements.UITextBox(manager=manager, relative_rect=pygame.Rect((950, 75), (400, 800)), container=menu_panel, object_id="#Top_Panel", html_text="")

description_box = pygame_gui.elements.UITextEntryBox(manager=manager, relative_rect=pygame.Rect((1400, 475), (500,400)), container=menu_panel, object_id="#Top_Panel")

forward_button = pygame_gui.elements.UIButton(manager=manager, relative_rect=pygame.Rect((475, 875), (250, 100)), text=">", container=menu_panel, object_id="#Help_Button")
backward_button = pygame_gui.elements.UIButton(manager=manager, relative_rect=pygame.Rect((225, 875), (250, 100)), text="<", container=menu_panel, object_id="#Help_Button")

# Code for generating the pieces
pieces = [
    *[Piece(i*100 + 75,   150, f"assets/pieces/b{piece}.png", piece, "B") for i, piece in enumerate('rnbqkbnr')],
    *[Piece(i*100 + 75, 250, f"assets/pieces/bP.png", 'p', "B") for i in range(8)],
    *[Piece(i*100 + 75, 750, f"assets/pieces/wP.png", 'P', "W") for i in range(8)],
    *[Piece(i*100 + 75, 850, f"assets/pieces/w{piece}.png", piece, "W") for i, piece in enumerate('RNBQKBNR')]
]

# ---------------------------------------------------

SQL_Query = f"SELECT Confidence_Score FROM Openings WHERE Opening_ID = {opening_id}"
ds_conf_score = db_cursor.execute(SQL_Query)

# Allows Drag and Drop Pieces.
dragging = False
dragged_piece = None

# Helps determine Refresh Rate
clock = pygame.time.Clock()
is_running = True
confidence_score = ds_conf_score


while is_running:
    
    time_delta = clock.tick(144)/1000.0 # may want to add an option to change this in future.
    # Main Event Listener
    for event in pygame.event.get():
        mx, my = pygame.mouse.get_pos() # Gets Mouse Pos
        if event.type == pygame.QUIT: # If the quit button is clicked stop running
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == home_button: # If the Home Button is clicked then go back to the menu

                is_running = False
            if event.ui_element == backward_button: # If the button is clicked remove the last move
                board.pop()
                print(board)
                print("Board Popped")
        #Checks whether the click was made within the chess board.
        if mx > 75 and my > 150 and mx < 875 and my < 950:
            if event.type == pygame.MOUSEBUTTONDOWN: # if within the chess board get the coordinates and convert that to a square the mouse is hovered on
                bx, by = pygame.mouse.get_pos()
                bfile = col_names[math.trunc((bx - 75) / 100)]
                brank = (9- (math.trunc((by - 150) / 100)+1))
                #for rect in pieces: # For dragging
                    #if rect.rect.collidepoint(bx, by):
                        #dragged_piece = rect
            elif event.type == pygame.MOUSEBUTTONUP: # WHen the mouse button is released
                #if dragged_piece is not None:
                    ax, ay = pygame.mouse.get_pos() # Get the Position of the mouse at this time
                    cx, cy = ax-150, ay-150 # Change the position to match the board
                    afile_num = math.trunc((ax - 75) / 100) # Find the file
                    afile = col_names[afile_num] # Find the letter of the file using a dictionary
                    arank = (9  - (math.trunc((ay - 150) / 100)+1)) # Find the Rank
                    #print(f"{brank} {arank}, {bfile} {afile}")
                    if brank != arank or bfile != afile: # Verifies whether a piece was moved 
                        for piece in pieces: # if so then move the piece
                            if piece.square == f"{bfile}{brank}":
                                move = f"{bfile}{brank}{afile}{arank}"
                                #print(board.legal_moves)
                                # Catches an error and doesn't allow the user to make an illegal move.
                                #try:
                                board.push_uci(move)
                                if board.is_valid() == True:
                                        print()
                                    # Here goes the update of the piece position as well as actually doing the move
                                        #print(board)
                                        # White Castling A bit much code but only allows legal castling
                                        
                                        if (move == "e1g1" or move == "e1h1") and board.has_kingside_castling_rights and piece.letter == "K":
                                            pieces[28].rect.x = 675
                                            pieces[28].square = "g1"
                                            pieces[31].rect.x = 575
                                            pieces[31].square = "f1"
                                        if (move == "e1c1" or move == "e1a1") and board.has_queenside_castling_rights and piece.letter == "K":
                                            pieces[28].rect.x = 275
                                            pieces[28].square = "c1"
                                            pieces[24].rect.x = 375
                                            pieces[24].square = "d1"
                                        # Black Castling
                                        if (move == "e8g8" or move == "e8h8") and board.has_kingside_castling_rights and piece.letter == "k":
                                            pieces[4].rect.x = 675
                                            pieces[4].square = "g8"
                                            pieces[7].rect.x = 575
                                            pieces[7].square = "f8"
                                        if (move == "e8c8"  or move == "e8a8") and board.has_queenside_castling_rights and piece.letter == "k":
                                            pieces[4].rect.x = 275
                                            pieces[4].square = "c8"
                                            pieces[0].rect.x = 375
                                            pieces[0].square = "d8"
                                        # Access and move the piece to the new square. Drag Animations come later.
                                        piece.rect.x = (afile_num * 100) + 75
                                        piece.rect.y = (math.trunc((ay + 50) / 100) * 100) - 50
                                        piece.square = f"{afile}{arank}"
                                        #update_text_box()
                                        move_string = board.move_stack
                                        update_board()
                                        #print(board.move_stack)
                                        dragged_piece = None
                                else:
                                        # If the move wasn't legal, remove it until they play a legal move
                                        print("Illegal")
                                        board.pop()
                                #print(f"Chosen Move = {bfile}{brank}{afile}{arank}, Piece = {piece.letter}")
                                #except:
                                #    print("Error")
                    else:
                        print("No Move Made")
                    #print(f"After x ={ax}, After y ={ay}")

                # Draw board position
                
            elif event.type == pygame.MOUSEMOTION:
                #mx, my = pygame.mouse.get_pos()
                for rect in pieces:
                        #dragged_piece.rect.y = my
                        #dragged_piece.rect.x = mx
                        # if you're hovered on a piece then change the mouse cursor
                        if rect.rect.collidepoint(event.pos):
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                            break
                        else:
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        manager.process_events(event)

    
    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    # Draws the actual board
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = COLOUR1
            else:
                color = COLOUR2
            pygame.draw.rect(window_surface, color, [col*100 + 75, (7-row)*100 + 150, 100, 100])

    # Draw pieces on screen
    for rect in pieces:
        window_surface.blit(rect.image, rect.rect)

 
    # Update the display.
    pygame.display.update()