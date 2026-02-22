import chess
import chess.engine
import pyperclip
import os
import sys
from GBUtils import dgt, menu
from src.constants import (
    VER, PGN_FILE_PATH, MNMAIN, SYMBOLS_TO_NAME, COLUMN_TO_NATO
)
from src.board import CustomBoard
from src.utils import (
    CalculateMaterial, SquaresListToString, InfoSquare, ExploreColumnsOrRows,
    GetPiecesPosition, GetPieceMoves, MoveToString
)
from src.pgn_handler import (
    LoadGamesFromPGN, NewGame, PastePGNFromClipboard, CopyPGNToClipboard,
    AppendGameToPGN, AddingPGNTAGS
)
from src.engine_handler import InitEngine, ShowStats
from src.interaction import ExplorerMode, BoardEditor

def main():
    print(f"Hi, it's Easyfish {VER}, here, by Gabriele Battaglia (IZ4APU).\n\tI'm ready to help you. Enjoy!")

    # Init
    engine, config = InitEngine()
    
    # Load Games
    existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
    print(f"Loaded {len(existing_games)} existing games in PGN database.")
    
    # New Game
    game, node = NewGame()
    board = CustomBoard()
    
    # State
    analysis_time = 2
    info = {} # Inizializzato vuoto
    multipv = 3
    prompt = "MOVE 1.: "
    fen_from_clip = ""

    while True:
        key_command = dgt(prompt=prompt, kind="s", smin=1, smax=8192)
        
        # Gestione input vuoto o solo spazi
        if not key_command:
            continue

        # Estrazione numero comando (es. per analisi)
        number_command_str = ''.join([char for char in key_command if char.isdigit()])
        number_command = int(number_command_str) if number_command_str else 0
        if number_command < 1: number_command = 1
        elif number_command > 600: number_command = 600

        # Comandi speciali (.)
        if key_command.startswith("."):
            cmd = key_command.lower()
            # Rimuovi numeri dal comando per il match
            cmd_clean = ''.join([char for char in cmd if not char.isdigit()])
            
            if cmd == ".q":
                break
            
            elif cmd == ".?":
                menu(d=MNMAIN, show=True)
            
            elif cmd == ".e":
                print("Entering Explorer mode...")
                ExplorerMode(game, engine)
                
            elif cmd == ".b":
                print(board)
                
            elif cmd == ".bm":
                white, black = CalculateMaterial(board)
                print(f"Material on the board: {white}/{black} White/Black")
                
            elif cmd == ".pt":
                AddingPGNTAGS(game)
                
            elif cmd == ".gp":
                CopyPGNToClipboard(game)
                
            elif cmd == ".pg":
                # PGN to Game
                print("Paste a new position from PGN in your system clipboard...")
                loaded_game = PastePGNFromClipboard()
                if loaded_game:
                    AppendGameToPGN(PGN_FILE_PATH, game, board) # Salva la precedente
                    game = loaded_game
                    node = game 
                    board = CustomBoard()
                    # Replay game to sync board state if needed, or just start from initial position
                    # Usually PGN load resets to start.
                    prompt = "START 1.: "
                    print("Game loaded successfully.")
                    print(board)
                else:
                    print("Invalid PGN or empty clipboard.")

            elif cmd == ".gf":
                pyperclip.copy(board.fen())
                print("Game to FEN. Copied to the clipboard")
                
            elif cmd == ".fg":
                # FEN to Game
                fen_from_clip = pyperclip.paste()
                if not fen_from_clip:
                    print("Sorry, your clipboard is empty. Please copy a valid FEN first.")
                else:
                    print("Paste a new position from FEN in your system clipboard.\n\tChecking FEN...")
                    try:
                        tmp_board = board.copy()
                        tmp_board.set_fen(fen_from_clip)
                        print("FEN is ok.")
                        AppendGameToPGN(PGN_FILE_PATH, game, board)
                        print("Current game saved.")
                        
                        existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
                        print(f"Loaded {len(existing_games)} existing games in PGN database.")
                        
                        board = CustomBoard()
                        board.set_fen(fen_from_clip)
                        
                        game, node = NewGame()
                        game.setup(board) 
                        
                        prompt = "START 1.: "
                        print(board)
                    except ValueError:
                        print("Invalid FEN string.")
                        
            elif cmd == ".n":
                print("Set up a new board from scratch. You're ready to go!")
                AppendGameToPGN(PGN_FILE_PATH, game, board)
                print("Old game saved.")
                existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
                print(f"Loaded {len(existing_games)} existing games in PGN database.")
                game, node = NewGame()
                board = CustomBoard()
                prompt = "START 1.: "
                
            elif cmd == ".be":
                AppendGameToPGN(PGN_FILE_PATH, game, board)
                existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
                game, node = NewGame()
                board = CustomBoard()
                fen = BoardEditor()
                board.set_fen(fen)
                game.setup(board)
                prompt = "START 1.: "
                
            elif cmd == ".ssf":
                os.startfile(config.get("path", ".")) # Apre la cartella, non il file JSON direttamente se non associato
                # Originale: os.startfile(CONFIG_FILE) -> apre il json col default editor.
                
            elif cmd == ".snl":
                multipv = dgt(prompt=f"Set a new number for analyses lines, now current to {multipv}: ", kind="i", imin=1, imax=256, default=3)
                print(multipv, "set.")
                
            elif cmd_clean == ".a": # cmd starts with .a
                if not engine:
                    print("Engine not loaded.")
                else:
                    sec = number_command if number_command > 0 else 1
                    print(f"Analyzing current position for {sec} seconds.")
                    limit = chess.engine.Limit(time=sec)
                    try:
                        info = engine.analyse(board, limit, multipv=multipv)
                        if isinstance(info, list):
                             ShowStats(board, info[0])
                        elif isinstance(info, dict):
                             ShowStats(board, info)
                    except Exception as e:
                        print(f"Analysis error: {e}")

            elif cmd_clean == ".l": # cmd starts with .l
                if info: 
                    idx = number_command - 1 if number_command > 0 else 0
                    if idx < 0: idx = 0
                    
                    current_info_list = info if isinstance(info, list) else [info]
                    
                    if idx >= len(current_info_list):
                        print(f"There are only {len(current_info_list)} analyses line available")
                        idx = len(current_info_list) - 1
                    
                    if idx == 0:
                        print("Best line:")
                    else:
                        print(f"{idx+1}° choice:")
                    
                    ShowStats(board, current_info_list[idx])

                else:
                    print("First you must do some analyses by sending .a command")
            
            else:
                print(f"Sorry but {cmd} is not a valid command.\nType '.?' for the menu.")

        # Comandi esplorazione pezzi (,)
        elif key_command.startswith(","):
            if len(key_command) > 1 and key_command[1] in SYMBOLS_TO_NAME:
                algebric = GetPiecesPosition(board, key_command[1])
                found = SYMBOLS_TO_NAME[key_command[1]]
                found += ": " + SquaresListToString(board, algebric)
                print(found)
            else:
                print(f"{key_command[1] if len(key_command)>1 else ''} is not a valid piece name")

        # Comandi esplorazione scacchiera (-)
        elif key_command.startswith("-"):
            cmd = key_command.lower()
            if len(cmd) == 3:
                square = cmd[-2:]
                if square[0] in "abcdefgh" and square[1] in "12345678":
                    print(InfoSquare(board, chess.parse_square(square)))
                else:
                    print("Not a valid square")
            elif len(cmd) == 2:
                if cmd[1] in "abcdefgh":
                    found_occupied_square = SquaresListToString(board, ExploreColumnsOrRows(board, ord(cmd[1])-97, vertical=True), True, True)
                    print(f"Pieces on column {COLUMN_TO_NATO[cmd[1]]} are: {found_occupied_square}")
                elif cmd[1] in "12345678":
                    found_occupied_square = SquaresListToString(board, ExploreColumnsOrRows(board, int(cmd[1])-1, vertical=False), True, True)
                    print(f"Pieces on row {cmd[1]} are: {found_occupied_square}")
            elif len(cmd) == 4:
                square = cmd[-2:]
                piece = key_command[1].upper() # Case sensitive originale
                
                if square[0] in "abcdefgh" and square[1] in "12345678" and piece in SYMBOLS_TO_NAME:
                     lm = False if board.piece_at(chess.parse_square(square)) else True
                     oos = False
                     legal_move_str = GetPieceMoves(board, piece, square, legal_moves=lm, occupied_only_square=oos)
                     print(f"{SYMBOLS_TO_NAME[piece][6:].capitalize()}'s moves from {COLUMN_TO_NATO[square[0]]} {square[1]} are: {legal_move_str}")
                else:
                    print("Piece's name or square not valid")
            else:
                print("not a valid exploration command")

        # Commenti (_)
        elif key_command.startswith("_"):
            node.comment = key_command[1:]
            print("Comment recorded.")

        # Mosse (SAN)
        else:
            move_input = key_command
            if move_input.lower() in ('o-o', 'oo', '00'): move_input = "O-O"
            elif move_input.lower() in ('o-o-o', 'ooo', '000'): move_input = "O-O-O"
            elif move_input[0].lower() in "rnqk": 
                move_input = move_input[0].upper() + move_input[1:]
            
            try:
                move = board.parse_san(move_input)
                print(MoveToString(board, move))
                board.push(move)
                node = node.add_main_variation(move)
                
                # Logic prompt originale
                if board.turn: # White turn (quindi il Nero ha appena mosso)
                     temp_move = board.pop()
                     last_san = board.san(temp_move)
                     board.push(temp_move)
                     prompt = f"{board.fullmove_number}... {last_san}: "
                else: # Black turn (quindi il Bianco ha appena mosso)
                     temp_move = board.pop()
                     last_san = board.san(temp_move)
                     board.push(temp_move)
                     prompt = f"{board.fullmove_number}. {last_san}: "

            except ValueError:
                print(f"{key_command}: illegal move.")

    # Exit
    AppendGameToPGN(PGN_FILE_PATH, game, board)
    updated_games = LoadGamesFromPGN(PGN_FILE_PATH)
    print(f"{len(updated_games)} games in PGN database at {PGN_FILE_PATH}.\n\tBye-Bye from Easyfish version {VER}, by Gabriele Battaglia (IZ4APU)\n\tsee you soon!")
    if engine:
        engine.quit()

if __name__ == "__main__":
    main()
