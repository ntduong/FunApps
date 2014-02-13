#!/usr/bin/python

""" Reversi (a.k.a Othello) game program.
    Computer vs Computer version.
    Author: Duong Nguyen
    Date: 2013/05/24
    
"""

import random
import sys

# CONSTANTS
NROWS = 8
NCOLS = 8

# BOARD-RELATED FUNCTIONS
#@profile
def get_blank_board(nr=8, nc=8):
    """ Get a blank board of size nr x nc.
        
        Params:
            nr: number of rows. Default: 8
            nc: number of columns. Default: 8
            
        Returns:
            A new blank board: a list of nr row lists, each row list is a list of nc elements.
    """
    assert nr % 2 == 0 and nc % 2 == 0, "The width and height of the board should be even!"
    #bBoard = []
	#for _ in xrange(nr):
    #    bBoard.append([' '] * nc)
    bBoard = [[' '] * nc for _ in xrange(nr)]   
    return bBoard 

#@profile
def init_board(board):
    """ Set the game board to initial state.
        
        Params:
            board: the game board to set to initial position.
            
        Returns:
            None
    """        
    nr = NROWS
    nc = NCOLS
    assert nr % 2 == 0 and nc % 2 == 0, "The width and height of the board should be even!"
    
    for r in xrange(nr):
        for c in xrange(nc):
			board[r][c] = ' '
	
	
    board[nr/2-1][nc/2-1] = board[nr/2][nc/2] = 'X'
    board[nr/2][nc/2-1] = board[nr/2-1][nc/2] = 'O'

#@profile
def get_board_copy(board):
    """ Copy the current game board.
        
        Params:
            board: the current board to copy
        
        Returns:
            copyBoard
    """
    nr = NROWS
    nc = NCOLS
    copyBoard = get_blank_board(nr=nr, nc=nc)
    
    for r in xrange(nr):
        for c in xrange(nc):
            copyBoard[r][c] = board[r][c]
    
    return copyBoard
     
def get_score_from_board(board):
    """ Get scores from current game board.
        Count the number of 'X' and 'O' in the current board.
        
        Params: 
            board: The current game board.
        
        Returns:
            A dictionary of score {'X': xscore, 'O': oscore} 
    """
    xscore = oscore = 0
    nr = NROWS
    nc = NCOLS
    for r in xrange(nr):
        for c in xrange(nc):
            if board[r][c] == 'X':
                xscore += 1
            if board[r][c] == 'O':
                oscore += 1
    return {'X': xscore, 'O': oscore}

# END BOARD-RELATED FUNCTIONS

# MOVE-RELATED FUNCTIONS
#@profile
def is_on_board(board, r, c):
    """ Check if (r,c) is located on the board.
        
        Params:
            r: row coordinate
            c: column coordinate
        
        Returns:
            True: if (r,c) is on the board.
            False: otherwise.
    """
    nr = NROWS
    nc = NCOLS
    return (0 <= r <= nr-1) and (0 <= c <= nc-1)
	
#@profile
def is_on_side(board, r, c):
    nr = NROWS
    nc = NCOLS
    return r == 0 or r == nr-1 or c == 0 or c == nc-1
	
#@profile
def is_corner(board, r, c):
    """ Check if (r,c) is a corner of the board.
        
        Params:
            r: row coordinate
            c: column coordinate
        
        Returns:
            True: if (r,c) is a corner of the board.
            False: otherwise.
    """
    nr = NROWS
    nc = NCOLS
    return (r == 0 and c == 0) or (r == 0 and c == nc-1) or (r == nr-1 and c == 0) or (r == nr-1 and c == nc-1)

#@profile
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
    if not cellsToFlip: # no cell to flip, then invalid move
        return False
    return cellsToFlip

#@profile   
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
    nr = NROWS
    nc = NCOLS
    for r in xrange(nr):
        for c in xrange(nc):
            if is_valid_move(board, symbol, r, c) != False:
                validMoves.append([r,c])
    return validMoves

# END MOVE-RELATED FUNCTIONS

# USER INTERACTION FUNCTIONS
def who_goes_first():
    """ Decide who (user or computer) will play first."""
    if random.randint(0,1) == 0:
        return 'computer'
    else:
        return 'player'
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

# AI FUNCTIONS
def get_random_move(board, symbol):
    """ Select random move from all valid moves."""
    return random.choice(get_valid_moves(board, symbol))

def get_basic_move(board, symbol):
    """ Basic strategy: Select the best score move."""
    possibleMoves = get_valid_moves(board, symbol)
    #random.shuffle(possibleMoves)
        
    # try all possible moves, get the best move with highest score.
    bestScore = -1
    for r, c in possibleMoves: 
        cBoard = get_board_copy(board)
        make_move(cBoard, symbol, r, c)
        score = get_score_from_board(board)[symbol]
        if score > bestScore: # update best score so far
            bestMove = [r, c]
            bestScore = score
            
    return bestMove

#@profile
def get_side_best_move(board, symbol):
    """ Select a side move.
        Fall back to the best score move if no side move available. 
    """
    possibleMoves = get_valid_moves(board, symbol)
    #random.shuffle(possibleMoves)
    
    for r, c in possibleMoves:
        if is_on_side(board, r, c):
            return [r,c]
    
    return get_basic_move(board, symbol)

#@profile
def get_corner_best_move(board, symbol):
    """ Select a corner move. 
        Fall back to the best score move if no corner move available.
    """
    possibleMoves = get_valid_moves(board, symbol)
    #random.shuffle(possibleMoves)
    
    for r, c in possibleMoves:
        if is_corner(board, r, c):
            return [r,c]
    
    return get_basic_move(board, symbol)

def get_corner_side_best_move(board, symbol):
    """ Select a corner move.
        If no corner move available, select a side move.
        If no side move available, select the best score move.
    """
    possibleMoves = get_valid_moves(board, symbol)
    #random.shuffle(possibleMoves)
    
    for r, c in possibleMoves:
        if is_corner(board, r, c):
            return [r,c]
        
    for r, c in possibleMoves:
        if is_on_side(board, r, c):
            return [r,c]
        
    return get_computer_move(board, symbol)

def get_side_corner_best_move(board, symbol):
    """ Select a side move.
        If no side move available, select a corner move.
        If no corner move available, select the best score move.
    """
    possibleMoves = get_valid_moves(board, symbol)
    #random.shuffle(possibleMoves)
        
    for r, c in possibleMoves:
        if is_on_side(board, r, c):
            return [r,c]
    
    for r, c in possibleMoves:
        if is_corner(board, r, c):
            return [r,c]
        
    return get_basic_move(board, symbol)

# HELPER FUNCTIONS
def show_points(board, playerSymbol, computerSymbol):
    """ Show current player and computer scores."""
    scores = get_score_from_board(board)
    print 'You have %s points.\nThe computer has %s points.' %(scores[playerSymbol], scores[computerSymbol])

def show_help():
    """ Show help info, such as how to play, etc."""
    print 'This is Reversi game.\nCheck Wikipedia page for the detailed rule.'

#@profile
def main():
    """ Main program for Othello game.
        Text-based user interface. 
        @todo: GUI version
    """
    #print 'Welcome to Reversi World!'
    
    xwins = 0
    owins = 0
    ties = 0
    #numGames = int(raw_input('Enter number of games to run: '))
    numGames = 10
    for game in xrange(numGames):
        #print 'Game #%s:' %(game),
        mainBoard = get_blank_board(nr=NROWS, nc=NCOLS)
        init_board(mainBoard)
        if who_goes_first() == 'player':
            turn = 'X'
        else:
            turn = 'O'
        
        while True:
            if turn == 'X':
                opponent = 'O'
                r, c = get_corner_best_move(mainBoard, 'X')
                make_move(mainBoard, 'X', r, c) 
            else:
                opponent = 'X'
                r, c = get_side_best_move(mainBoard, 'O')
                make_move(mainBoard, 'O', r, c)
            
            if get_valid_moves(mainBoard, opponent) == []:
                break
            else:
                turn = opponent
            
        scores = get_score_from_board(mainBoard)
        #print 'X scored %s points. O scored %s points.' % (scores['X'], scores['O'])
        if scores['X'] > scores['O']:
            xwins += 1
        elif scores['O'] > scores['X']:
            owins += 1
        else:
            ties += 1
        
    xpercent = round(xwins*100./numGames, 2)
    opercent = round(owins*100./numGames, 2)
    tiepercent = round(ties*100./numGames, 2)
    '''
    print 'X wins %s games (%s %%)\nO wins %s games (%s %%)\nTies for %s games (%s %%).' \
            %(xwins, xpercent, owins, opercent, ties, tiepercent)
    '''
    
if __name__ == '__main__':
    main()