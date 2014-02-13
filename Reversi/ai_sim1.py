#!/usr/bin/python

""" Reversi (a.k.a Othello) game program.
    Computer vs Computer version.
    Author: Duong Nguyen
    Date: 2013/05/24
    
"""

import random
import sys

# BOARD-RELATED FUNCTIONS
def draw_board(board):
    """ Print the current game board (text-based).
        
        Params:
            board: the game board to print out. 
            
        Returns:
            None
    """
    nr = len(board)
    nc = len(board[0])
    colNames = map(str, range(1, nc+1)) # column names: '1',...'nc'
    HLINE = ' ' * 3 + '---'.join(['+'] * (nc+1))
    VLINE = ' ' * 3 + (' ' * 3).join(['|'] * (nc+1))
    
    print ' ' * 5 + (' ' * 3).join(colNames)
    print HLINE
    for r in range(nr):
        print VLINE
        print "%d " %(r+1),
        for c in range(nc):
            print '| %s' %(board[r][c]),
        print '|'
        print VLINE
        print HLINE
    
def get_blank_board(nr=8, nc=8):
    """ Get a blank board of size nr x nc.
        
        Params:
            nr: number of rows. Default: 8
            nc: number of columns. Default: 8
            
        Returns:
            A new blank board: a list of nr row lists, each row list is a list of nc elements.
    """
    assert nr % 2 == 0 and nc % 2 == 0, "The width and height of the board should be even!"
    bBoard = []
    for _ in range(nr):
        bBoard.append([' '] * nc)
        
    return bBoard 
    
def init_board(board):
    """ Set the game board to initial state.
        
        Params:
            board: the game board to set to initial position.
            
        Returns:
            None
    """        
    nr = len(board)
    nc = len(board[0])
    assert nr % 2 == 0 and nc % 2 == 0, "The width and height of the board should be even!"
    
    for r in range(nr):
        for c in range(nc):
            board[r][c] = ' '
            
    board[nr/2-1][nc/2-1] = board[nr/2][nc/2] = 'X'
    board[nr/2][nc/2-1] = board[nr/2-1][nc/2] = 'O'
    
def get_board_copy(board):
    """ Copy the current game board.
        
        Params:
            board: the current board to copy
        
        Returns:
            copyBoard
    """
    nr = len(board)
    nc = len(board[0])
    copyBoard = get_blank_board(nr=nr, nc=nc)
    
    for r in range(nr):
        for c in range(nc):
            copyBoard[r][c] = board[r][c]
    
    return copyBoard
     
def get_board_with_valid_moves(board, symbol):
    """ Show valid move hints."""
    cBoard = get_board_copy(board)
    for r,c in get_valid_moves(cBoard, symbol):
        cBoard[r][c] = '.'
    return cBoard

def get_score_from_board(board):
    """ Get scores from current game board.
        Count the number of 'X' and 'O' in the current board.
        
        Params: 
            board: The current game board.
        
        Returns:
            A dictionary of score {'X': xscore, 'O': oscore} 
    """
    xscore = oscore = 0
    nr = len(board)
    nc = len(board[0])
    for r in range(nr):
        for c in range(nc):
            if board[r][c] == 'X':
                xscore += 1
            if board[r][c] == 'O':
                oscore += 1
    return {'X': xscore, 'O': oscore}

# END BOARD-RELATED FUNCTIONS

# MOVE-RELATED FUNCTIONS
def is_on_board(board, r, c):
    """ Check if (r,c) is located on the board.
        
        Params:
            r: row coordinate
            c: column coordinate
        
        Returns:
            True: if (r,c) is on the board.
            False: otherwise.
    """
    nr = len(board)
    nc = len(board[0])
    return (0 <= r <= nr-1) and (0 <= c <= nc-1)

def is_corner(board, r, c):
    """ Check if (r,c) is a corner of the board.
        
        Params:
            r: row coordinate
            c: column coordinate
        
        Returns:
            True: if (r,c) is a corner of the board.
            False: otherwise.
    """
    nr = len(board)
    nc = len(board[0])
    return (r == 0 and c == 0) or (r == 0 and c == nc-1) or (r == nr-1 and c == 0) or (r == nr-1 and c == nc-1)

def is_valid_move(board, symbol, r, c):
    """ Check if a move (r,c) is valid for the current player.
        The validity of a move is defined by the rule of Othello (Reversi) game.
        See for example, http://en.wikipedia.org/wiki/Reversi for the detailed rules.
        
        Params:
            board: the current game board
            symbol: the current player symbol ('X' or 'O')
            r,c: a move coordinates to check.
            
        Returns:
            A (non-empty) list of cells to flip if this move is valid.
            False if this move is invalid.
    """
    if board[r][c] != ' ' or not is_on_board(board, r, c):
        return False
    
    board[r][c] = symbol # temporarily set the symbol on the board
    
    if symbol == 'X':
        opponent = 'O'
    else:
        opponent = 'X'
    
    cellsToFlip = [] # list of cells to flip after this move
    for dr, dc in [[0,1],[0,-1],[1,1],[1,0],[1,-1],[-1,1],[-1,0],[-1,-1]]:
        cur_r, cur_c = r, c
        cur_r += dr
        cur_c += dc
        if is_on_board(board, cur_r, cur_c) and board[cur_r][cur_c] == opponent:
            cur_r += dr
            cur_c += dc
            if not is_on_board(board, cur_r, cur_c):
                continue
            while board[cur_r][cur_c] == opponent:
                cur_r += dr
                cur_c += dc
                if not is_on_board(board, cur_r, cur_c):
                    break
            if not is_on_board(board, cur_r, cur_c):
                continue
            if board[cur_r][cur_c] == symbol: # valid move
                while True: # backtrack to get flip cells
                    cur_r -= dr
                    cur_c -= dc
                    if cur_r == r and cur_c == c:
                        break
                    cellsToFlip.append([cur_r, cur_c])
        
    board[r][c] = ' ' # restore to empty cell
    if len(cellsToFlip) == 0: # no cell to flip, then invalid move
        return False
    return cellsToFlip
    
def get_valid_moves(board, symbol):
    """ Get all valid moves for a player given the current board.
        This function is used for hints or decide computer move.
        
        Params:
            board: the current game board
            symbol: current player symbol
            
        Returns:
            A list of (r,c) coordinates for valid moves
    """
    validMoves = []
    nr = len(board)
    nc = len(board[0])
    for r in range(nr):
        for c in range(nc):
            if is_valid_move(board, symbol, r, c) != False:
                validMoves.append([r,c])
    return validMoves

# END MOVE-RELATED FUNCTIONS

# USER INTERACTION FUNCTIONS
def select_symbol():
    """ Determine players' symbols.
        Get input from user to decide type of symbol for players: 'X' or 'O'
        
        Params: 
            None
            
        Returns:
            [User symbol, Computer symbol]
    """
    symbol = ''
    while not (symbol == 'X' or symbol == 'O'):
        print 'Please choose X or O:'
        symbol = raw_input().upper()
        
    if symbol == 'X':
        return ['X', 'O']
    else:
        return ['O', 'X']
    
def who_goes_first():
    """ Decide who (user or computer) will play first."""
    if random.randint(0,1) == 0:
        return 'computer'
    else:
        return 'player'
    
def play_again():
    """ Ask user to play again or quit the game."""
    print 'Do you want to play again? (yes(Y) or no(N))'
    return raw_input().lower().startswith('y')

# END USER INTERACTION FUNCTIONS

# GAME FUNCTIONS
def make_move(board, symbol, r, c):
    """ Make a move: put symbol at (r,c) cell, 
        and update board after this move.
        
        Params:
            board: current game board.
            symbol: the current turn (player symbol or computer symbol)
            r, c: coordinates of the move.
            
        Returns:
            True if move successfully.
            False if otherwise.
    """
    # First, check the validity of this move
    cellsToFlip = is_valid_move(board, symbol, r, c)
    if cellsToFlip == False:
        return False
    
    # Update game board
    board[r][c] = symbol
    for fr, fc in cellsToFlip:
        board[fr][fc] = symbol
    return True

def get_player_move(board, playerSymbol):
    """ Get player's input:
        + a next move
        + hint
        + quit game

        Returns:
            [r,c] if player enters a next move.
            'hint' if player enters 'hints'
            'quit' if player enters 'quit'
    """
    nr = len(board)
    nc = len(board[0])
    
    ROWS = map(str, range(1, nr+1))
    COLS = map(str, range(1, nc+1))
    while True:
        print "Enter your move [r,c] coordinates, or 'quit' to end the game, or 'hints' to turn off/on hints."
        move = raw_input().lower()
        if move == 'quit':
            return 'quit'
        if move == 'hints':
            return 'hints'
        if len(move) == 2 and move[0] in ROWS and move[1] in COLS:
            r = int(move[0]) - 1
            c = int(move[1]) - 1
            if is_valid_move(board, playerSymbol, r, c) == False:
                continue
            else:
                break
        else:
            print 'Invalid move!'
            print 'Please enter row number in range [1, %d] and column number in range [1, %d].' %(nr, nc)
            
    return [r,c]
    
def get_computer_move(board, computerSymbol):
    """ Given the current board and computerSymbol, 
        decide computer's next move (AI part)
        
        Params:
            board: the current game board.
            computerSymbol: computer symbol ('X' or 'O')
            
        Returns:
            A list of moves.
    """
    possibleMoves = get_valid_moves(board, computerSymbol)
    random.shuffle(possibleMoves)
    for r, c in possibleMoves:
        if is_corner(board, r, c): # choose a corner if possible
            return [r, c]
        
    # try all possible moves, get the best move with highest score.
    bestScore = -1
    for r, c in possibleMoves: 
        cBoard = get_board_copy(board)
        make_move(cBoard, computerSymbol, r, c)
        score = get_score_from_board(board)[computerSymbol]
        if score > bestScore: # update best score so far
            bestMove = [r, c]
            bestScore = score
            
    return bestMove

def show_points(board, playerSymbol, computerSymbol):
    """ Show current player and computer scores."""
    scores = get_score_from_board(board)
    print 'You have %s points.\nThe computer has %s points.' %(scores[playerSymbol], scores[computerSymbol])

def show_help():
    """ Show help info, such as how to play, etc."""
    print 'This is Reversi game.\nCheck Wikipedia page for the detailed rule.'

def main():
    """ Main program for Othello game.
        Text-based user interface. 
        @todo: GUI version
    """
    
    NROWS = 8
    NCOLS = 8
    print 'Welcome to Reversi World!'

    while True:
        mainBoard = get_blank_board(nr=NROWS, nc=NCOLS)
        init_board(mainBoard)
        if who_goes_first() == 'player':
            turn = 'X'
        else:
            turn = 'O'
        
        print 'The ' + turn + ' will go first!'
        
        while True:
            draw_board(mainBoard)
            scores = get_score_from_board(mainBoard)
            print 'X has %s points.\nO has %s points' %(scores['X'], scores['O'])
            raw_input('Press Enter to continue.')
            if turn == 'X':
                opponent = 'O'
                r, c = get_computer_move(mainBoard, 'X')
                make_move(mainBoard, 'X', r, c) 
            else:
                opponent = 'X'
                r, c = get_computer_move(mainBoard, 'O')
                make_move(mainBoard, 'O', r, c)
            
            if get_valid_moves(mainBoard, opponent) == []:
                break
            else:
                turn = opponent
            
        draw_board(mainBoard)
        scores = get_score_from_board(mainBoard)
        print 'X scored %s points. O scored %s points.' % (scores['X'], scores['O'])
        if not play_again():
            print 'Goodbye. See you again!'
            break
        
if __name__ == '__main__':
    main()