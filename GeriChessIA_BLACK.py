#El usuario juega con negras
import time
import random
import pandas as pd
import os
from time import sleep
import random
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtCore import Qt

import chess
import chess.svg
import chess.syzygy
import chess.pgn

#importacions per l'assistent (si es fan)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Definir dimensiones de la ventana
        self.setGeometry(100, 100, 800, 800)

        # Crear layout principal vertical
        main_layout = QVBoxLayout()

        # Crear layout para el tablero
        self.board_layout = QVBoxLayout()

        # Crear widget SVG para el tablero de ajedrez
        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.board_layout.addWidget(self.widgetSvg)

        # Añadir el tablero al layout principal con espaciadores para centrarlo
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(self.board_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Crear layout horizontal para botones y otros controles
        button_layout = QHBoxLayout()

        # Añadir un espaciador flexible a la izquierda del botón para centrarlo
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Crear botón de reinicio y añadirlo al layout horizontal
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.on_button_click)
        button_layout.addWidget(self.reset_button)

        # Añadir un espaciador flexible a la derecha del botón para centrarlo
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Añadir el layout de botones al layout principal
        main_layout.addLayout(button_layout)

        # Establecer el layout en la ventana principal
        self.setLayout(main_layout)
        
        # Inicializar el tablero
        self.chessboard = chess.Board()
        self.update_board()
      
    def on_button_click(self):
        # Resetea el tablero visual y el estado interno del juego
        print("Juego reseteado")
        global board, i  # Acceder al objeto 'board' globalmente
        board.reset()  # Reiniciar el tablero global
        i = 0  # Reiniciar el contador de turnos
        self.chessboard.reset()  # Reiniciar el tablero de la interfaz gráfica
        # Actualizar el SVG del tablero después del reinicio
        self.chessboardSvg = chess.svg.board(self.chessboard).encode("UTF-8")
        self.widgetSvg.load(self.chessboardSvg)
        app.processEvents()
        
    def update_board(self):
        # Actualizar el SVG del tablero con las dimensiones correctas
        board_size = min(self.widgetSvg.width(), self.widgetSvg.height())  # Asegurar que sea cuadrado
        self.chessboardSvg = chess.svg.board(self.chessboard, size=board_size).encode("UTF-8")
        self.widgetSvg.load(self.chessboardSvg)

    def resizeEvent(self, event):
        # Determinar el tamaño cuadrado para el tablero (el mínimo entre ancho y alto)
        board_size = min(900, 7500)

        # Establecer el tamaño cuadrado del tablero
        self.widgetSvg.setFixedSize(board_size, board_size)

        # Actualizar el SVG del tablero con el nuevo tamaño
        self.update_board()

        # Llamar al evento de redimensionado base
        super().resizeEvent(event)
       
# =============================================================================
# Función de evaluación de tablero
# =============================================================================
#Valor de peces
def getPieceValue(piece):
    """Asigna un valor a las piezas según su tipo."""
    if piece is None:
        return 0

    value = 0
    symbol = piece.symbol()

    # Valores básicos de las piezas
    if symbol == "P" or symbol == "p":
        value = -10
    elif symbol == "N" or symbol == "n":
        value = -30
    elif symbol == "B" or symbol == "b":
        value = -30
    elif symbol == "R" or symbol == "r":
        value = -50
    elif symbol == "Q" or symbol == "q":
        value = -90
    elif symbol == "K" or symbol == "k":
        value = -900

    # Multiplicar por -1 si es una pieza negra
    if piece.color == chess.BLACK:
        value = -value

    return value

# Evaluar el control del centro
def evaluate_center_control(board):
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    control = 0
    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            control += getPieceValue(piece) // -10  # Aumentar ligeramente el valor si controla el centro
    return control

# Evaluar la estructura de peones
def evaluate_pawn_structure(board):
    # Aquí podrías agregar criterios como peones aislados, doblados o pasados.
    # Por ahora, simplificaremos evaluando el número de peones en el tablero.
    pawns = len(board.pieces(chess.PAWN, chess.WHITE)) - len(board.pieces(chess.PAWN, chess.BLACK))
    return pawns * -10  # Ajustar el valor según la importancia de la estructura de peones

# Evaluar la seguridad del rey
def evaluate_king_safety(board):
    # La seguridad del rey puede depender de cuántas piezas lo protegen y si está enrocado.
    safety = 0
    if board.has_kingside_castling_rights(chess.WHITE):
        safety += 50  # El enroque mejora la seguridad del rey
    if board.has_kingside_castling_rights(chess.BLACK):
        safety -= 50
    return safety

# Evaluar la movilidad
def evaluate_mobility(board):
    mobility = len(list(board.legal_moves))
    return mobility

# Función principal de evaluación
def evaluation(board):
    evaluation = 0

    # Sumar el valor de las piezas
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        evaluation += getPieceValue(piece)

    # Añadir factores adicionales a la evaluación
    evaluation -= evaluate_center_control(board)  # Control del centro
    evaluation -= evaluate_pawn_structure(board)  # Estructura de peones
    evaluation -= evaluate_king_safety(board)     # Seguridad del rey
    evaluation -= evaluate_mobility(board)        # Movilidad

    return evaluation

# =============================================================================
# Implementación del algoritmo Minimax con poda alpha-beta
# =============================================================================
def minimax(depth, board, alpha, beta, is_maximizing):
    if(depth==0):
        return -evaluation(board)
    possibleMoves = board.legal_moves
    if(is_maximizing):
        bestMove = -9999
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x)) 
            board.push(move)
            bestMove = max(bestMove, minimax(depth-1, board,alpha,beta, not is_maximizing))
            board.pop()
            alpha = max(alpha,bestMove)
            if beta<= alpha:
                return bestMove
        return bestMove
    else:
        bestMove = 9999
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            bestMove = min(bestMove, minimax(depth-1, board, alpha, beta, not is_maximizing))
            board.pop()
            beta = min(beta, bestMove)
            if (beta<= alpha):
                return bestMove
        return bestMove

def bestMove(board, depth):
    best_move = None
    best_value = -9999
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(depth - 1, board, -10000, 10000, False)
        board.pop()
        if board_value > best_value:
            best_value = board_value
            best_move = move
    return best_move

# =============================================================================
# Implementación del movimiento del bot utilizando Minimax
# =============================================================================
def BOT_MOVE(board, player_move):
    
    #Si no se accede a las bases de datos usa el algoritmo
    depth = 3  # Ajusta la profundidad según la potencia deseada del bot
    bot_move = bestMove(board, depth)
    
    if bot_move is None:
        return '', board

    # Convertir el movimiento en notación SAN (Standard Algebraic Notation)
    bot_move = board.san(bot_move)

    # Verificar si se necesita promoción de peón
    if pawn_promotion(board, bot_move):
        # Promocionar a reina por defecto
        board.push_san(bot_move + 'q')
    else:
        board.push_san(bot_move)

    # Actualizar y mostrar el tablero
    window.update_board()
    app.processEvents()  # Refrescar la interfaz
    
    chessboardSvg = chess.svg.board(board, flipped=True).encode("UTF-8")
    window.widgetSvg.load(chessboardSvg)
    app.processEvents()

    return bot_move, board, app.processEvents() and print("Posición FEN actual:", board.fen())

 
#=================================================================================================  
#DEFINIR JUGADA DEL JUGADOR
#================================================================================================
def USER_MOVE(board):
    if board.is_checkmate():
        last_move = board.peek()  # Obtener el último movimiento sin modificar el tablero
        winner = "White" if board.turn == chess.BLACK else "Black"
        print("Winner:", winner)

        # Devolver el objeto board para evitar el error en BOT_MOVE
        return '', board  # Asegúrate de devolver el objeto board, no un string
    else:
        legal_moves = [move.uci() for move in board.legal_moves]
        while True:
            try:
                player_move = input("Your move:")
                if not pawn_promotion(board, player_move):
                    board.push_san(player_move)
                else:
                    promotion_piece = input("Piece to promote to (Q, R, K, B):")
                    board.push_san(player_move + promotion_piece)
                break
            except ValueError or player_move not in legal_moves:
                print("Illegal move. Try again.")
                
            # Actualizar el tablero después del movimiento del usuario
            window.update_board()
            app.processEvents()  # Refrescar la interfaz
            
            chessboardSvg = chess.svg.board(board, flipped=False).encode("UTF-8")
            window.widgetSvg.load(chessboardSvg)
            app.processEvents()
            

        return player_move, board 
    
# =============================================================================
#   Comprovación de si hay coronación o no
# =============================================================================
def pawn_promotion(board, move):
    # Verificar si el movimiento tiene la longitud correcta
    if len(move) < 4:
        return False

    # Extraer las posiciones inicial y final
    start_square = move[:2]  # Dos primeros caracteres
    end_square = move[2:4]   # Dos siguientes caracteres

    # Analizar el cuadrado inicial
    try:
        start = chess.parse_square(start_square)
        end = chess.parse_square(end_square)
    except ValueError as e:
        print(f"Error en el movimiento: {move}. Detalles: {e}")
        return False

    piece = board.piece_at(start)

    # Verificar si es un peón que está en la fila de promoción
    if piece and piece.piece_type == chess.PAWN:
        if (piece.color == chess.WHITE and chess.square_rank(end) == 7) or \
           (piece.color == chess.BLACK and chess.square_rank(end) == 0):
            return True

    return False


# =============================================================================
# START THE GAME
# =============================================================================

if __name__ == "__main__":
    app = QApplication([])

    # Configurar el tablero de ajedrez
    board = chess.Board()
    i = 0

    # Crear la ventana principal
    window = MainWindow()

    chessboardSvg = chess.svg.board(board, flipped=True).encode("UTF-8")
    window.widgetSvg.load(chessboardSvg)
    window.show()
    app.processEvents()
    
    # Bucle principal del juego
    while not board.is_game_over():  # Verificar si el juego ha terminado
        i += 1
        print("Turno número " + str(i))
        
        # Mover las piezas blancas (bot)
        print("El bot (blancas) está pensando...")
        bot_move = BOT_MOVE(board, None)
            # Actualizar y mostrar el tablero
        window.update_board()
        app.processEvents()  # Refrescar la interfaz
        
        chessboardSvg = chess.svg.board(board, flipped=True).encode("UTF-8")
        window.widgetSvg.load(chessboardSvg)
        app.processEvents()
        
        # Verificar si el juego ha terminado después del movimiento del bot
        if board.is_game_over():
            break

        # Mover las piezas negras (usuario)
        player_move, board = USER_MOVE(board)
        window.update_board()
        app.processEvents()  # Refrescar la interfaz
        
        chessboardSvg = chess.svg.board(board, flipped=True).encode("UTF-8")
        window.widgetSvg.load(chessboardSvg)
        app.processEvents()
        # Verificar si el juego ha terminado después del movimiento del usuario
        if board.is_game_over():
            break
    
    # El bucle ha terminado, limpiar o mostrar mensaje
    print("El juego ha terminado.")
    app.quit()