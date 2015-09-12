#!/usr/bin/env python
# -*- coding: utf-8 -*-

# *******************************************
# **           Miguel Pinto                **
# **           Nuno Azevedo                **
# **           21/05/2015                  **
# **           Sistemas Multimedia         **
# *******************************************

from Tkinter import *
import chess.uci
import time
import Image
import os
import platform

# Jogador 0 - Pretas  - Letras Minusculas
# Jogador 1 - Brancas - Letras Maiusculas

engine = chess.uci.popen_engine('stockfish-6-linux/Linux/stockfish_6_x64')
engine.uci()

class GameBoard(Frame):
    def __init__(self, parent, rows = 8, columns = 8, size = 62, color1 = '#F6D992', color2 = '#833030'):
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}

        canvas_width = columns * size
        canvas_height = rows * size

        Frame.__init__(self, parent)
        self.canvas = Canvas(self, borderwidth = 0, highlightthickness = 0, width = canvas_width, height = canvas_height, background = 'bisque')
        self.canvas.pack(side = 'top', fill = 'both', expand = True, padx = 2, pady = 2)

        self.canvas.bind('<Configure>', self.refresh)

    def addpiece(self, name, image, row = 0, column = 0):
        self.canvas.create_image(0, 0, image = image, tags = (name, 'piece'), anchor = 'c')
        self.placepiece(name, row, column)

    def placepiece(self, name, row, column):
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def refresh(self, event):
        xsize = int((event.width - 1) / self.columns)
        ysize = int((event.height - 1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete('square')
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline = 'black', fill = color, tags = 'square')
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces: self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise('piece')
        self.canvas.tag_lower('square')

root = Tk()
root.wm_title('Multimedia Systems Chess')
root.resizable(width = FALSE, height = FALSE)
visualboard = GameBoard(root)
clicked = False
modclick = False
square1 = ''
square2 = ''

convert = { 'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7, '1':7, '2':6, '3':5, '4':4, '5':3, '6':2, '7':1, '8':0 }

pieces = { (0, 0):'r', (0, 1):'n', (0, 2):'b', (0, 3):'q', (0, 4):'k', (0, 5):'b1', (0, 6):'n1', (0, 7):'r1', (1, 0):'p', (1, 1):'p1', (1, 2):'p2', (1, 3):'p3', (1, 4):'p4', (1, 5):'p5', (1, 6):'p6', (1, 7):'p7', (7, 0):'R', (7, 1):'N', (7, 2):'B', (7, 3):'Q', (7, 4):'K', (7, 5):'B1', (7, 6):'N1', (7, 7):'R1', (6, 0):'P', (6, 1):'P1', (6, 2):'P2', (6, 3):'P3', (6, 4):'P4', (6, 5):'P5', (6, 6):'P6', (6, 7):'P7' }

squares = { (0, 61, 0, 61):'a8', (61, 122, 0, 61):'b8', (122, 183, 0, 61):'c8', (183, 244, 0, 61):'d8', (244, 305, 0, 61):'e8', (305, 366, 0, 61):'f8', (366, 427, 0, 61):'g8', (427, 488, 0, 61):'h8', (0, 61, 61, 122):'a7', (61, 122, 61, 122):'b7', (122, 183, 61, 122):'c7', (183, 244, 61, 122):'d7', (244, 305, 61, 122):'e7', (305, 366, 61, 122):'f7', (366, 427, 61, 122):'g7', (427, 488, 61, 122):'h7', (0, 61, 122, 183):'a6', (61, 122, 122, 183):'b6', (122, 183, 122, 183):'c6', (183, 244, 122, 183):'d6', (244, 305, 122, 183):'e6', (305, 366, 122, 183):'f6', (366, 427, 122, 183):'g6', (427, 488, 122, 183):'h6', (0, 61, 183, 244):'a5', (61, 122, 183, 244):'b5', (122, 183, 183, 244):'c5', (183, 244, 183, 244):'d5', (244, 305, 183, 244):'e5', (305, 366, 183, 244):'f5', (366, 427, 183, 244):'g5', (427, 488, 183, 244):'h5', (0, 61, 244, 305):'a4', (61, 122, 244, 305):'b4', (122, 183, 244, 305):'c4', (183, 244, 244, 305):'d4', (244, 305, 244, 305):'e4', (305, 366, 244, 305):'f4', (366, 427, 244, 305):'g4', (427, 488, 244, 305):'h4', (0, 61, 305, 366):'a3', (61, 122, 305, 366):'b3', (122, 183, 305, 366):'c3', (183, 244, 305, 366):'d3', (244, 305, 305, 366):'e3', (305, 366, 305, 366):'f3', (366, 427, 305, 366):'g3', (427, 488, 305, 366):'h3', (0, 61, 366, 427):'a2', (61, 122, 366, 427):'b2', (122, 183, 366, 427):'c2', (183, 244, 366, 427):'d2', (244, 305, 366, 427):'e2', (305, 366, 366, 427):'f2', (366, 427, 366, 427):'g2', (427, 488, 366, 427):'h2', (0, 61, 427, 488):'a1', (61, 122, 427, 488):'b1', (122, 183, 427, 488):'c1', (183, 244, 427, 488):'d1', (244, 305, 427, 488):'e1', (305, 366, 427, 488):'f1', (366, 427, 427, 488):'g1', (427, 488, 427, 488):'h1' }

image = PhotoImage(file = 'images/rP.png')
visualboard.addpiece('r', image, 0, 0)
image1 = PhotoImage(file = 'images/nP.png')
visualboard.addpiece('n', image1, 0, 1)
image2 = PhotoImage(file = 'images/bP.png')
visualboard.addpiece('b', image2, 0, 2)
image3 = PhotoImage(file = 'images/qP.png')
visualboard.addpiece('q', image3, 0, 3)
image4 = PhotoImage(file = 'images/kP.png')
visualboard.addpiece('k', image4, 0, 4)
image5 = PhotoImage(file = 'images/bP.png')
visualboard.addpiece('b1', image5, 0, 5)
image6 = PhotoImage(file = 'images/nP.png')
visualboard.addpiece('n1', image6, 0, 6)
image7 = PhotoImage(file = 'images/rP.png')
visualboard.addpiece('r1', image7, 0, 7)
image8 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p', image8, 1, 0)
image9 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p1', image9, 1, 1)
image10 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p2', image10, 1, 2)
image11 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p3', image11, 1, 3)
image12 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p4', image12, 1, 4)
image13 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p5', image13, 1, 5)
image14 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p6', image14, 1, 6)
image15 = PhotoImage(file = 'images/pP.png')
visualboard.addpiece('p7', image15, 1, 7)

image16 = PhotoImage(file = 'images/rB.png')
visualboard.addpiece('R', image16, 7, 0)
image17 = PhotoImage(file = 'images/nB.png')
visualboard.addpiece('N', image17, 7, 1)
image18 = PhotoImage(file = 'images/bB.png')
visualboard.addpiece('B', image18, 7, 2)
image19 = PhotoImage(file = 'images/qB.png')
visualboard.addpiece('Q', image19, 7, 3)
image20 = PhotoImage(file = 'images/kB.png')
visualboard.addpiece('K', image20, 7, 4)
image21 = PhotoImage(file = 'images/bB.png')
visualboard.addpiece('B1', image21, 7, 5)
image22 = PhotoImage(file = 'images/nB.png')
visualboard.addpiece('N1', image22, 7, 6)
image23 = PhotoImage(file = 'images/rB.png')
visualboard.addpiece('R1', image23, 7, 7)
image24 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P', image24, 6, 0)
image25 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P1', image25, 6, 1)
image26 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P2', image26, 6, 2)
image27 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P3', image27, 6, 3)
image28 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P4', image28, 6, 4)
image29 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P5', image29, 6, 5)
image30 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P6', image30, 6, 6)
image31 = PhotoImage(file = 'images/pB.png')
visualboard.addpiece('P7', image31, 6, 7)

def callback(event):
    global square1
    global square2
    for coords in squares:
        if coords[0] < event.x and event.x < coords[1] and coords[2] < event.y and event.y < coords[3]:
            square1 = square2
            square2 = squares[coords]

def startGameAIvsH():
    Label(root).grid(row = 22, columnspan = 4)
    Label(root, text = 'First Player:', font = 'bold').grid(row = 23, column = 0, sticky = W)
    e = Entry(root)
    e.grid(row = 23, column = 1, columnspan = 2, sticky = W)
    Label(root, text = '( 1  -  Human  |  2  -  AI )', font = 'bold').grid(row = 23, column = 2, columnspan = 3, sticky = E)
    global clicked
    if not clicked:
        Label(root, text = 'Difficulty:', font = 'bold').grid(row = 24, column = 0, sticky = W)
        Button(root, text = 'Easy', width = 12, command = lambda: jogo_AIvsH(int(e.get()) - 1, 0)).grid(row = 24, column = 1)
        Button(root, text = 'Medium', width = 12, command = lambda: jogo_AIvsH(int(e.get()) - 1, 3)).grid(row = 24, column = 2)
        Button(root, text = 'Hard', width = 12, command = lambda: jogo_AIvsH(int(e.get()) - 1, 6)).grid(row = 24, column = 3)
        clicked = True

def startGameAIvsAI():
    global clicked
    if not clicked:
        Label(root).grid(row = 22, columnspan = 4)
        Label(root, text = 'Difficulty:', font = 'bold').grid(row = 23, column = 0, sticky = W)
        Button(root, text = 'Easy', width = 12, command = lambda: jogo_AIvsAI(0)).grid(row = 23, column = 1)
        Button(root, text = 'Medium', width = 12, command = lambda: jogo_AIvsAI(3)).grid(row = 23, column = 2)
        Button(root, text = 'Hard', width = 12, command = lambda: jogo_AIvsAI(6)).grid(row = 23, column = 3)
        clicked = True

def challenges():
    global clicked
    if not clicked:
        Label(root).grid(row = 22, columnspan = 4)
        Button(root, text = 'Queen Down', width = 12, command = startMode1).grid(row = 23, column = 0)
        Button(root, text = 'Survival', width = 12, command = startMode2).grid(row = 23, column = 1)
        Button(root, text = 'Material Check', width = 12, command = startMode3).grid(row = 23, column = 2)
        Button(root, text = 'Material Difference', width = 12, command = startMode4).grid(row = 23, column = 3)
        clicked = True

def startMode1():
    global modclick
    if not modclick:
        Label(root).grid(row = 24, columnspan = 4)
        Label(root, text = 'Challenge:', font = 'bold').grid(row = 25, column = 0, sticky = W)
        Label(root, text = 'Conquer the opponent queen in less than X plays').grid(row = 25, column = 1, columnspan = 3, sticky = W)
        Label(root, text = 'First Player:', font = 'bold').grid(row = 26, column = 0, sticky = W)
        e = Entry(root)
        e.grid(row = 26, column = 1, columnspan = 2, sticky = W)
        Label(root, text = '( 1  -  Human  |  2  -  AI )', font = 'bold').grid(row = 26, column = 2, columnspan = 3, sticky = E)
        Label(root).grid(row = 27, columnspan = 4)
        Label(root, text = 'Difficulty:', font = 'bold').grid(row = 27, column = 0, sticky = W)
        Button(root, text = 'Easy (20 Plays)', width = 12, command = lambda: modo1(int(e.get()) - 1, 0, 20)).grid(row = 27, column = 1)
        Button(root, text = 'Medium (15 Plays)', width = 12, command = lambda: modo1(int(e.get()) - 1, 3, 15)).grid(row = 27, column = 2)
        Button(root, text = 'Hard (10 Plays)', width = 12, command = lambda: modo1(int(e.get()) - 1, 9, 10)).grid(row = 27, column = 3)
        modclick = True

def startMode2():
    global modclick
    if not modclick:
        Label(root).grid(row = 24, columnspan = 4)
        Label(root, text = 'Challenge:', font = 'bold').grid(row = 25, column = 0, sticky = W)
        Label(root, text = 'Survive for X plays').grid(row = 25, column = 1, sticky = W)
        Label(root, text = 'First Player:', font = 'bold').grid(row = 26, column = 0, sticky = W)
        e = Entry(root)
        e.grid(row = 26, column = 1, columnspan = 2, sticky = W)
        Label(root, text = '( 1  -  Human  |  2  -  AI )', font = 'bold').grid(row = 26, column = 2, columnspan = 3, sticky = E)
        Label(root).grid(row = 27, columnspan = 4)
        Label(root, text = 'Difficulty:', font = 'bold').grid(row = 27, column = 0, sticky = W)
        Button(root, text = 'Easy (10 Plays)', width = 12, command = lambda: modo2(int(e.get()) - 1, 0, 10)).grid(row = 27, column = 1)
        Button(root, text = 'Medium (25 Plays)', width = 12, command = lambda: modo2(int(e.get()) - 1, 3, 25)).grid(row = 27, column = 2)
        Button(root, text = 'Hard (40 Plays)', width = 12, command = lambda: modo2(int(e.get()) - 1, 9, 40)).grid(row = 27, column = 3)
        modclick = True

def startMode3():
    global modclick
    if not modclick:
        Label(root).grid(row = 24, columnspan = 4)
        Label(root, text = 'Challenge:', font = 'bold').grid(row = 25, column = 0, sticky = W)
        Label(root, text = 'Make a check having material advantage').grid(row = 25, column = 1, columnspan = 2, sticky = W)
        Label(root, text = 'First Player:', font = 'bold').grid(row = 26, column = 0, sticky = W)
        e = Entry(root)
        e.grid(row = 26, column = 1, columnspan = 2, sticky = W)
        Label(root, text = '( 1  -  Human  |  2  -  AI )', font = 'bold').grid(row = 26, column = 2, columnspan = 3, sticky = E)
        Label(root).grid(row = 27, columnspan = 4)
        Label(root, text = 'Difficulty:', font = 'bold').grid(row = 27, column = 0, sticky = W)
        Button(root, text = 'Easy', width = 12, command = lambda: modo3(int(e.get()) - 1, 0)).grid(row = 27, column = 1)
        Button(root, text = 'Medium', width = 12, command = lambda: modo3(int(e.get()) - 1, 3)).grid(row = 27, column = 2)
        Button(root, text = 'Hard', width = 12, command = lambda: modo3(int(e.get()) - 1, 9)).grid(row = 27, column = 3)
        modclick = True

def startMode4():
    global modclick
    if not modclick:
        Label(root).grid(row = 24, columnspan = 4)
        Label(root, text = 'Challenge:', font = 'bold').grid(row = 25, column = 0, sticky = W)
        Label(root, text = 'Having material advantage higher than 5 points').grid(row = 25, column = 1, columnspan = 3, sticky = W)
        Label(root, text = 'First Player:', font = 'bold').grid(row = 26, column = 0, sticky = W)
        e = Entry(root)
        e.grid(row = 26, column = 1, columnspan = 2, sticky = W)
        Label(root, text = '( 1  -  Human  |  2  -  AI )', font = 'bold').grid(row = 26, column = 2, columnspan = 3, sticky = E)
        Label(root).grid(row = 27, columnspan = 4)
        Label(root, text = 'Difficulty:', font = 'bold').grid(row = 27, column = 0, sticky = W)
        Button(root, text = 'Easy', width = 12, command = lambda: modo3(int(e.get()) - 1, 0)).grid(row = 27, column = 1)
        Button(root, text = 'Medium', width = 12, command =  lambda: modo3(int(e.get()) - 1, 3)).grid(row = 27, column = 2)
        Button(root, text = 'Hard', width = 12, command =lambda: modo3(int(e.get()) - 1, 9)).grid(row = 27, column = 3)
        modclick = True

def pieceAt(pos, board):
    index = 0
    str = 'none'
    for i in range(len(chess.SQUARE_NAMES)):
        name = chess.SQUARE_NAMES[i]
        if pos == name: index = i
    tipo = board.piece_type_at(index)
    if tipo != 0:
        peca = board.piece_at(index)
        str = chess.Piece.symbol(peca)
    return str

def pieceInBoard(p, board):
    lst = []
    for square in chess.SQUARES:
        tipo = board.piece_type_at(square)
        if tipo != 0:
            peca = board.piece_at(square)
            str = chess.Piece.symbol(peca)
            lst.append(str)
    if p in lst: return True
    return False

def piecesOnBoard(board):
    lst = []
    for square in chess.SQUARES:
        tipo = board.piece_type_at(square)
        if tipo != 0:
            peca = board.piece_at(square)
            str = chess.Piece.symbol(peca)
            lst.append(str)
    return lst

def count_pecas(pecas_jogo):
    #                [P, N, B, R, Q, K, p, n, b, r, q, k]
    contador_pecas = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for peca in pecas_jogo:
        if peca == 'P': contador_pecas[0] += 1
        elif peca == 'N': contador_pecas[1] += 1
        elif peca == 'B': contador_pecas[2] += 1
        elif peca == 'R': contador_pecas[3] += 1
        elif peca == 'Q': contador_pecas[4] += 1
        elif peca == 'K': contador_pecas[5] += 1
        elif peca == 'p': contador_pecas[6] += 1
        elif peca == 'n': contador_pecas[7] += 1
        elif peca == 'b': contador_pecas[8] += 1
        elif peca == 'r': contador_pecas[9] += 1
        elif peca == 'q': contador_pecas[10] += 1
        elif peca == 'k': contador_pecas[11] += 1
    return contador_pecas

def count_pontos(jogador, lst_pecas, board):
    # Peao = 1, Bispo = 3, Cavalo = 3, Torre = 5, Rainha = 9
    contador_pecas = count_pecas(lst_pecas)
    pontos = 0
    if jogador == 0:
        pontos += contador_pecas[0] * 1  # Peoes
        pontos += contador_pecas[1] * 3  # Cavalos
        pontos += contador_pecas[2] * 3  # Bispos
        pontos += contador_pecas[3] * 5  # Torres
        pontos += contador_pecas[4] * 9  # Rainha
    else:
        pontos += contador_pecas[6] * 1  # Peoes
        pontos += contador_pecas[7] * 3  # Cavalos
        pontos += contador_pecas[8] * 3  # Bispos
        pontos += contador_pecas[9] * 5  # Torres
        pontos += contador_pecas[10] * 9 # Rainha
    return pontos

def modo1(jog, dificuldade, n_jogadas): # Conquistar a Rainha em menos de X jogadas
    root.bind('<Button-1>', callback)

    board = chess.Board()
    estado = 0
    while pieceInBoard('q', board):
        Label(root, text = 'Plays: ' + str(board.fullmove_number - 1)).grid(row = 25, column = 3, sticky = E)

        if board.fullmove_number == n_jogadas:
            estado = 3
            break
        if board.is_checkmate():
            estado = 2
            break
        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        if board.turn == jog:
            play = chess.Move.from_uci('a1a1')
            while not play in board.legal_moves:
                global square1
                global square2
                raw_input()
                var = square1 + square2
                if len(var) == 4: play = chess.Move.from_uci(var)

            x1 = int(convert[var[:2][::-1][0]])
            y1 = int(convert[var[:2][::-1][1]])
            x2 = int(convert[var[2:][::-1][0]])
            y2 = int(convert[var[2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(play)

        else:
            engine.position(board)
            bestmove, ponder = engine.go(movetime = (125 * dificuldade))

            x1 = int(convert[str(bestmove)[:4][:2][::-1][0]])
            y1 = int(convert[str(bestmove)[:4][:2][::-1][1]])
            x2 = int(convert[str(bestmove)[:4][2:][::-1][0]])
            y2 = int(convert[str(bestmove)[:4][2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(bestmove)

    if estado == 1: Label(root, text = 'Draw. You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    elif estado == 2: Label(root, text = 'You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    elif estado == 3: Label(root, text = 'You lost. The number of plays was reached!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'You have completed the challenge in ' + str(board.fullmove_number) + ' plays!', font = 'bold').grid(row = 10, columnspan = 8)

def modo2(jog, dificuldade, n_jogadas): # Sobreviver durante X jogadas
    root.bind('<Button-1>', callback)

    board = chess.Board()
    estado = 0
    while board.fullmove_number < n_jogadas:
        Label(root, text = 'Plays: ' + str(board.fullmove_number - 1)).grid(row = 25, column = 3, sticky = E)

        if board.is_checkmate():
            estado = 2
            break
        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        if board.turn == jog:
            play = chess.Move.from_uci('a1a1')
            while not play in board.legal_moves:
                global square1
                global square2
                raw_input()
                var = square1 + square2
                if len(var) == 4: play = chess.Move.from_uci(var)

            x1 = int(convert[var[:2][::-1][0]])
            y1 = int(convert[var[:2][::-1][1]])
            x2 = int(convert[var[2:][::-1][0]])
            y2 = int(convert[var[2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(play)

        else:
            engine.position(board)
            bestmove, ponder = engine.go(movetime = (125 * dificuldade))

            x1 = int(convert[str(bestmove)[:4][:2][::-1][0]])
            y1 = int(convert[str(bestmove)[:4][:2][::-1][1]])
            x2 = int(convert[str(bestmove)[:4][2:][::-1][0]])
            y2 = int(convert[str(bestmove)[:4][2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(bestmove)

    if estado == 1: Label(root, text = 'Draw. You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    elif estado == 2: Label(root, text = 'You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'You have completed the challenge!', font = 'bold').grid(row = 10, columnspan = 8)

def modo3(jog, dificuldade):            # Estar em Vantagem Material e dar um Check
    root.bind('<Button-1>', callback)

    board = chess.Board()
    estado = 0
    while True:
        if board.is_checkmate():
            estado = 2
            break
        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        if board.turn == jog:
            play = chess.Move.from_uci('a1a1')
            while not play in board.legal_moves:
                global square1
                global square2
                raw_input()
                var = square1 + square2
                if len(var) == 4: play = chess.Move.from_uci(var)

            x1 = int(convert[var[:2][::-1][0]])
            y1 = int(convert[var[:2][::-1][1]])
            x2 = int(convert[var[2:][::-1][0]])
            y2 = int(convert[var[2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(play)

        else:
            lst_pecas = piecesOnBoard(board)
            pontos0 = count_pontos(0, lst_pecas,board)
            pontos1 = count_pontos(1, lst_pecas,board)
            if ((jog == 0 and pontos0 >= pontos1) or (jog == 1 and pontos1 >= pontos0)) and board.is_check():
                estado = 3
                break

            engine.position(board)
            bestmove, ponder = engine.go(movetime = (125 * dificuldade))

            x1 = int(convert[str(bestmove)[:4][:2][::-1][0]])
            y1 = int(convert[str(bestmove)[:4][:2][::-1][1]])
            x2 = int(convert[str(bestmove)[:4][2:][::-1][0]])
            y2 = int(convert[str(bestmove)[:4][2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(bestmove)

    if estado == 1: Label(root, text = 'Draw. You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    elif estado == 2: Label(root, text = 'You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'You have completed the challenge!', font = 'bold').grid(row = 10, columnspan = 8)

def modo4(jog, dificuldade):            # Estar em Vantagem Material por uma diferenca de 5 pontos
    root.bind('<Button-1>', callback)

    board = chess.Board()
    estado = 0
    while True:
        lst_pecas = lst_pecas_jogo(board)
        pontos0 = count_pontos(0, lst_pecas, board)
        pontos1 = count_pontos(1, lst_pecas, board)
        if (jog == 0 and pontos0 >= pontos1 + 5) or (jog == 1 and pontos1 >= pontos0 + 5):
            estado = 3
            break
        if board.is_checkmate():
            estado = 2
            break
        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        if board.turn == jog:
            play = chess.Move.from_uci('a1a1')
            while not play in board.legal_moves:
                global square1
                global square2
                raw_input()
                var = square1 + square2
                if len(var) == 4: play = chess.Move.from_uci(var)

            x1 = int(convert[var[:2][::-1][0]])
            y1 = int(convert[var[:2][::-1][1]])
            x2 = int(convert[var[2:][::-1][0]])
            y2 = int(convert[var[2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(play)

        else:
            engine.position(board)
            bestmove, ponder = engine.go(movetime = (125 * dificuldade))

            x1 = int(convert[str(bestmove)[:4][:2][::-1][0]])
            y1 = int(convert[str(bestmove)[:4][:2][::-1][1]])
            x2 = int(convert[str(bestmove)[:4][2:][::-1][0]])
            y2 = int(convert[str(bestmove)[:4][2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(bestmove)

    if estado == 1: Label(root, text = 'Draw. You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    elif estado == 2: Label(root, text = 'You lost the challenge!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'You have completed the challenge!', font = 'bold').grid(row = 10, columnspan = 8)

def jogo_HvsH():                        # Humano vs Humano
    root.bind('<Button-1>', callback)

    board = chess.Board()
    estado = 0
    while not board.is_checkmate():
        if board.turn == 0: Label(root, text = 'White Player').grid(row = 10, columnspan = 8)
        else: Label(root, text = 'Black Player').grid(row = 10, columnspan = 8)

        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        play = chess.Move.from_uci('a1a1')
        while not play in board.legal_moves:
            global square1
            global square2
            raw_input()
            var = square1 + square2
            if len(var) == 4: play = chess.Move.from_uci(var)

        x1 = int(convert[var[:2][::-1][0]])
        y1 = int(convert[var[:2][::-1][1]])
        x2 = int(convert[var[2:][::-1][0]])
        y2 = int(convert[var[2:][::-1][1]])
        try:
            visualboard.placepiece(pieces[(x1, y1)], x2, y2)
            if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
            pieces[(x2, y2)] = pieces[(x1, y1)]
            del pieces[(x1, y1)]
        except: pass
        board.push(play)

    if estado == 1: Label(root, text = 'It\'s a Draw!', font = 'bold').grid(row = 10, columnspan = 8)
    elif board.turn == 0: Label(root, text = 'Black Player Wins!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'White Player Wins!', font = 'bold').grid(row = 10, columnspan = 8)

def jogo_AIvsH(jog, dificuldade):       # Computador vs Humano
    root.bind('<Button-1>', callback)

    board = chess.Board()
    estado = 0
    while not board.is_checkmate():
        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        if board.turn == jog:
            play = chess.Move.from_uci('a1a1')
            while not play in board.legal_moves:
                global square1
                global square2
                raw_input()
                var = square1 + square2
                if len(var) == 4: play = chess.Move.from_uci(var)

            x1 = int(convert[var[:2][::-1][0]])
            y1 = int(convert[var[:2][::-1][1]])
            x2 = int(convert[var[2:][::-1][0]])
            y2 = int(convert[var[2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(play)

        else:
            engine.position(board)
            bestmove, ponder = engine.go(movetime = (125 * dificuldade))

            x1 = int(convert[str(bestmove)[:4][:2][::-1][0]])
            y1 = int(convert[str(bestmove)[:4][:2][::-1][1]])
            x2 = int(convert[str(bestmove)[:4][2:][::-1][0]])
            y2 = int(convert[str(bestmove)[:4][2:][::-1][1]])
            try:
                visualboard.placepiece(pieces[(x1, y1)], x2, y2)
                if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
                pieces[(x2, y2)] = pieces[(x1, y1)]
                del pieces[(x1, y1)]
            except: pass
            board.push(bestmove)

    if estado == 1: Label(root, text = 'It\'s a Draw!', font = 'bold').grid(row = 10, columnspan = 8)
    elif board.turn == 0: Label(root, text = 'Black Player Wins!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'White Player Wins!', font = 'bold').grid(row = 10, columnspan = 8)

def jogo_AIvsAI(dificuldade):           # Computador vs Computador
    board = chess.Board()
    estado = 0
    while not board.is_checkmate():
        if (board.is_game_over() and not board.is_checkmate()) or board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repitition() or board.is_seventyfive_moves():
            estado = 1
            break

        engine.position(board)
        bestmove, ponder = engine.go(movetime = (125 * dificuldade))

        x1 = int(convert[str(bestmove)[:4][:2][::-1][0]])
        y1 = int(convert[str(bestmove)[:4][:2][::-1][1]])
        x2 = int(convert[str(bestmove)[:4][2:][::-1][0]])
        y2 = int(convert[str(bestmove)[:4][2:][::-1][1]])
        try:
            visualboard.placepiece(pieces[(x1, y1)], x2, y2)
            if (x2, y2) in pieces: visualboard.canvas.delete(pieces[(x2, y2)])
            pieces[(x2, y2)] = pieces[(x1, y1)]
            del pieces[(x1, y1)]
        except: pass
        board.push(bestmove)
        print board, "\n"

    if estado == 1: Label(root, text = 'It\'s a Draw!', font = 'bold').grid(row = 10, columnspan = 8)
    elif board.turn == 0: Label(root, text = 'Black Player Wins!', font = 'bold').grid(row = 10, columnspan = 8)
    else: Label(root, text = 'White Player Wins!', font = 'bold').grid(row = 10, columnspan = 8)

    countP = countB = 0
    for square in chess.SQUARES:
        if pieceAt(chess.SQUARE_NAMES[square], board) == 'r': countP += 1
        elif pieceAt(chess.SQUARE_NAMES[square], board) == 'R': countB += 1
    if countP == 0:
        visualboard.canvas.delete('r')
        visualboard.canvas.delete('r1')
    if countB == 0:
        visualboard.canvas.delete('R')
        visualboard.canvas.delete('R1')
    if countP == 1: visualboard.canvas.delete('r1')
    if countB == 1: visualboard.canvas.delete('R1')

def on_closing():
    if platform.system() == 'Linux': os.system('clear')
    else: os.system('cls')
    print '\nThanks for using our app :)\n'
    root.destroy()
    exit()

visualboard.grid(rowspan = 20, columnspan = 20)
Button(root, text = 'Human vs Human', width = 12, command = jogo_HvsH).grid(row = 21, column = 0)
Button(root, text = 'Human vs AI', width = 12, command = startGameAIvsH).grid(row = 21, column = 1)
Button(root, text = 'AI vs AI', width = 12, command = startGameAIvsAI).grid(row = 21, column = 2)
Button(root, text = 'Challenges', width = 12, command = challenges).grid(row = 21, column = 3)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
