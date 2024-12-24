#bot con tablero en SVG el ususario juega con negras
#Gerard Llonch Farrés 23/09/2024 gerard.llonch07@gmail.com
#Tauler amb clicks

import pandas as pd
from time import sleep
import random
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint

import chess
import chess.svg
import chess.pgn


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeriChessIA")
        # Definir dimensions de la finestra
        self.setGeometry(100, 100, 800, 800)
        # Crear layout principal vertical
        main_layout = QVBoxLayout()
        # Crear layout per al tauler
        self.board_layout = QVBoxLayout()
        # Crear widget SVG per al tauler d'escacs
        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.board_layout.addWidget(self.widgetSvg)
        # Afegir el tauler al layout principal amb espaiadors per centrar-lo
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(self.board_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # Crear layout horizontal per a botons
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # Crear botó de reinici i afegir-lo al layout horitzontal
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.on_button_click)
        button_layout.addWidget(self.reset_button)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addLayout(button_layout)
        # Establir el layout a la finestra principal
        self.setLayout(main_layout)
        # Inicialitzar el tabuler
        self.chessboard = chess.Board()
        self.update_board()
    
    # Conectar el evento de clic al tablero
        self.widgetSvg.mousePressEvent = self.handle_mouse_click

    def handle_mouse_click(self, event):
        try: 
            if event.button() == Qt.LeftButton:
                position = event.pos()
                square = self.get_square_from_click(position)
                
                if self.selected_square is None:
                    # Primera selección
                    self.selected_square = square
                else:
                    # Segunda selección, intentar mover
                    move = chess.Move.from_uci(self.selected_square + square)
                    if move in self.chessboard.legal_moves:
                        self.chessboard.push(move)
                        self.update_board()
                    else:
                        print("Movimiento ilegal")
                    self.selected_square = None  # Resetear selección
        except chess.InvalidMoveError as e:
        # Manejar el caso de movimiento inválido (como seleccionar la misma casilla)
            print(f"Error: Movimiento inválido: {e}")
        

    def get_square_from_click(self, position: QPoint) -> str:
        board_size = min(self.widgetSvg.width(), self.widgetSvg.height())
        square_size = board_size / 8
        x = position.x() // square_size
        y = position.y() // square_size
        # Convertir a notación UCI
        file = chr(int(x) + ord('a'))
        rank = str(8 - int(y))
        return file + rank
      
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

#Primera valoració
def getPieceValue(piece):
    """Asigna un valor a las piezas según su tipo."""
    if piece is None:
        return 0
    value = 0
    symbol = piece.symbol()

    # Valors bàsics de les peces
    if symbol == "P" or symbol == "p":
        value = 10
    elif symbol == "N" or symbol == "n":
        value = 30
    elif symbol == "B" or symbol == "b":
        value = 30
    elif symbol == "R" or symbol == "r":
        value = 50
    elif symbol == "Q" or symbol == "q":
        value = 90
    elif symbol == "K" or symbol == "k":
        value = 900

    # Multiplicar per -1 si es una peça negra
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
            control += getPieceValue(piece) // 10  # Aumentar ligeramente el valor si controla el centro
    return control

# Evaluar la estructura de peones
def evaluate_pawn_structure(board):
    # Aquí podrías agregar criterios como peones aislados, doblados o pasados.
    # Por ahora, simplificaremos evaluando el número de peones en el tablero.
    pawns = len(board.pieces(chess.PAWN, chess.WHITE)) - len(board.pieces(chess.PAWN, chess.BLACK))
    return pawns * 10  # Ajustar el valor según la importancia de la estructura de peones

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

# Funció principal d'avaluació
def evaluation(board):
    evaluation = 0

    # Sumar el valor de les peces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        evaluation += getPieceValue(piece)

    # Altres factors de la funció d'avaluació
    evaluation += evaluate_center_control(board)  # Control del centre
    evaluation += evaluate_pawn_structure(board)  # Estructura de peons
    evaluation += evaluate_king_safety(board)     # Seguretat del rei
    evaluation += evaluate_mobility(board)        # Mobilitat

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
    
    chessboardSvg = chess.svg.board(board, flipped=False).encode("UTF-8")
    window.widgetSvg.load(chessboardSvg)
    app.processEvents()

    return bot_move, board and print("Posición FEN actual:", board.fen())

#=================================================================================================  
#DEFINIR JUGADA DEL JUGADOR
#================================================================================================
def USER_MOVE(board):
    """Permite al usuario realizar su movimiento mediante clics con el ratón."""
    print("Es tu turno. Haz clic en las casillas para mover.")

    def handle_click(event):
        try:
            nonlocal selected_square, move_done
            
            if event.button() == Qt.LeftButton:
                position = event.pos()
                square = get_square_from_click(position)

                if selected_square is None:
                    # Primera selección: guardar la casilla inicial
                    selected_square = square
                    print(f"Casilla inicial seleccionada: {square}")
                else:
                    try:
                    # Segunda selección: intentar realizar el movimiento
                        move = chess.Move.from_uci(selected_square + square)
                        if move in board.legal_moves:
                            board.push(move)
                            move_done = True  # Marcar que el movimiento se ha completado
                            print(f"Movimiento realizado: {selected_square + square}")
                        else:
                            print("Movimiento ilegal, selecciona nuevamente.")
                        selected_square = None  # Reiniciar la selección
                    except chess.InvalidMoveError:
                        print(f"Error: Movimiento inválido al intentar mover de {selected_square} a {square}.")
                        selected_square = None  # Reiniciar la selección si el movimiento es inválido
                        return  # Salir de la función sin cambiar el estado
        except ValueError as e:
            print(f"Error: {e}")
            selected_square = None  # Reiniciar la selección si ocurre un error
    
        
    def get_square_from_click(position):
        """Convierte la posición del clic en una casilla en notación UCI."""
    
        board_size = min(window.widgetSvg.width(), window.widgetSvg.height())
        square_size = board_size / 8
        x = int(position.x() // square_size)
        y = int(position.y() // square_size)
        # Convertir a notación UCI
        file = chr(x + ord('a'))
        rank = str(8 - y)
        return file + rank

    # Variables internas para controlar el movimiento
    selected_square = None
    move_done = False

    # Conectar el evento de clic
    window.widgetSvg.mousePressEvent = handle_click

    # Esperar a que el usuario complete su movimiento
    while not move_done:
        app.processEvents()  # Permitir que PyQt procese eventos

    # Actualizar el tablero después del movimiento del usuario
    window.update_board()
    return board.peek().uci(), board  # Retornar el último movimiento y el estado actualizado del tablero
    
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

    chessboardSvg = chess.svg.board(board, flipped=False).encode("UTF-8")
    window.widgetSvg.load(chessboardSvg)
    window.show()
    app.processEvents()
    
    # Bucle principal del juego
    while not board.is_game_over():  # Verificar si el juego ha terminado
        i += 1
        print("Turno número " + str(i))
        
        # Mover las piezas negras (bot)
        bot_move = BOT_MOVE(board, None)
        chessboardSvg = chess.svg.board(board, flipped=False).encode("UTF-8")
        window.widgetSvg.load(chessboardSvg)
        app.processEvents()
        # Verificar si el juego ha terminado después del movimiento del bot
        if board.is_game_over():
            break
        
        # Mover las piezas blancas (usuario)
        player_move, board = USER_MOVE(board)
        chessboardSvg = chess.svg.board(board, flipped=False).encode("UTF-8")
        window.widgetSvg.load(chessboardSvg)
        app.processEvents()
        # Verificar si el juego ha terminado después del movimiento del usuario
        if board.is_game_over():
            break
    
    # El bucle ha terminado, limpiar o mostrar mensaje
    print("El juego ha terminado.")
    app.quit()
