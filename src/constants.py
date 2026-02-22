import os
import chess

# Version info
VER="0.22.0, Feb 22nd, 2026"  # Updated version for refactoring start

# File paths
CONFIG_FILE = "easyfish.json"
PGN_FILE_PATH = "Easyfish games collection.pgn"

# Defaults
DEFAULT_EVENT="Having fun with Easyfish"
DEFAULT_SITE=os.getenv('COMPUTERNAME')+"'s PC"
DEFAULT_ROUND="-"
DEFAULT_WHITE_SURENAME="White"
DEFAULT_WHITE_FIRSTNAME="Gabe"
DEFAULT_BLACK_SURENAME="Black"
DEFAULT_BLACK_FIRSTNAME="Ginny"

# Chess conversion maps
COLUMN_TO_NATO = {
    'a': "alpha",
    'b': "bravo",
    'c': "charlie",
    'd': "delta",
    'e': "echo",
    'f': "foxtrot",
    'g': "golf",
    'h': "hotel"}

CHESSPIECE_TO_NAME = {
    chess.PAWN: "Pawn",
    chess.KNIGHT: "Knight",
    chess.BISHOP: "Bishop",
    chess.ROOK: "Rook",
    chess.QUEEN: "Queen",
    chess.KING: "King"}

PIECE_VALUES={
    'R':5,
    'r':5,
    'N':3,
    'n':3,
    'B':3,
    'b':3,
    'Q':9,
    'q':9,
    'P':1,
    'p':1,
    'K':0,
    'k':0}

SAN_CHESSPIECES = {
    'P': chess.PAWN, 'N': chess.KNIGHT, 'B': chess.BISHOP,
    'R': chess.ROOK, 'Q': chess.QUEEN, 'K': chess.KING,
    'p': chess.PAWN, 'n': chess.KNIGHT, 'b': chess.BISHOP,
    'r': chess.ROOK, 'q': chess.QUEEN, 'k': chess.KING}

SYMBOLS_TO_NAME={
    'R':'White rook',
    'r':'Black rook',
    'N':'White knight',
    'n':'Black knight',
    'B':'White bishop',
    'b':'Black bishop',
    'Q':'White queen',
    'q':'Black queen',
    'K':'White king',
    'k':'Black king',
    'P':'White pawn',
    'p':'Black pawn'}

# Menus
MNMAIN={'.q':'Quit the application',
        '.?':'To show this menu',
        '_[comment]':'To add a comment to the current move',
        '.a#':"Analyse the position for # seconds",
        '.b':'To see the board',
        '.be':'Board Editor',
        '.bm':'Board material balance',
        '.e':'Explorer mode',
        '.fg':'FEN to Game. Paste from clipboard',
        '.gf':'Game to FEN, copy to clipboard',
        '.gp':'Game to PGN. Copy to clipboard',
        '.pg':'PGN to Game. Paste from clipboard',
        '.l#':'View Analysis Line/Lines',
        '.n':'New game from Scratch',
        '.pt':'Set PGN Tags for current game',
        '.snl':'Set Number of Analysis Lines',
        '.ssf':"Show Settings File",
        ',[piece]':"Any piece's name to locate it/them",
        '-[piecesquare]':"Piece and square to see its movements",
        '-[column]':"A to H column to know which pieces are on",
        '-[row]':"1 to 8 row to know which pieces are on",
        '[move]':'Any legal chess move in SAN format, e.g. d4'}

MNEXPLORER={'a':'Go to preview move',
            'd':'Go to next move',
            'w':'Up (variant selection only)',
            'x':'Down (variant selection only)',
            'q':'Jump to first move',
            'e':'Jump to last move',
            'z':'Exit current variant',
            'c':'Show the comment again',
            's':'Perform analyses',
            'r':'Set number of seconds for analyses',
            '?':'To see this help',
            '[esc]':'Go back to the main menu'}
