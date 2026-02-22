# Easyfish: a CLI app to play and analysis with an UCI engine.
# Data di concepimento 10/06/2024 di Gabriele Battaglia
# Moved on Github on june 26th, 2024. My first project there.

#QI
from GBUtils import dgt, menu, key
from datetime import datetime
import chess, chess.engine, chess.pgn, os, json, multiprocessing, pyperclip, io

#QCostants
VER="0.21.2, June 27th, 2024"
CONFIG_FILE = "easyfish.json"
PGN_FILE_PATH = "Easyfish games collection.pgn"
DEFAULT_EVENT="Having fun with Easyfish"
DEFAULT_SITE=os.getenv('COMPUTERNAME')+"'s PC"
DEFAULT_ROUND="-"
DEFAULT_WHITE_SURENAME="White"
DEFAULT_WHITE_FIRSTNAME="Gabe"
DEFAULT_BLACK_SURENAME="Black"
DEFAULT_BLACK_FIRSTNAME="Ginny"
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

#QClass
class CustomBoard(chess.Board):
	def __str__(self):
		board_str = "FEN: "+str(board.fen())+"\n"
		white_material,black_material=CalculateMaterial(board)
		ranks = range(8, 0, -1) if self.turn == chess.WHITE else range(1, 9)
		files = range(8) if self.turn == chess.WHITE else range(7, -1, -1)
		for rank in ranks:
			board_str += str(rank)
			for file in files:
				square = chess.square(file, rank - 1)
				piece = self.piece_at(square)
				if piece:
					symbol = piece.symbol()
					if piece.color == chess.WHITE:
						board_str += symbol.upper()
					else:
						board_str += symbol.lower()
				else:
					board_str += "-" if (rank + file) % 2 == 0 else "+"
			board_str += "\n"
		board_str += " abcdefgh" if self.turn == chess.WHITE else " hgfedcba"
		if self.fullmove_number == 1 and self.turn == chess.WHITE:
			last_move_info = "1.???"
		else:
			last_move_color = "White" if self.turn == chess.BLACK else "Black"
			move_number = self.fullmove_number - (1 if self.turn == chess.WHITE else 0)
			if self.move_stack:
				temp_board = chess.Board()
				for move in self.move_stack[:-1]:
					temp_board.push(move)
				last_move_san = temp_board.san(self.move_stack[-1])
			else:
				last_move_san = "???"
			if self.turn == chess.BLACK:
				last_move_info = f"{move_number}. {last_move_san}"
			else:
				last_move_info = f"{move_number}... {last_move_san}"
		board_str += f" {last_move_info} Material: {white_material}/{black_material}"
		return board_str

#QFunc
def CopyPGNToClipboard(game):
	pgn_io = io.StringIO()
	exporter = chess.pgn.StringExporter(pgn_io)
	game.accept(exporter)
	pgn_string = pgn_io.getvalue()
	pyperclip.copy(pgn_string)
	print("PGN game copied to clipboard.")
	return
def PastePGNFromClipboard():
	pgn_string = pyperclip.paste()
	pgn_io = io.StringIO(pgn_string)
	game = chess.pgn.read_game(pgn_io)
	return game
def NewGame():
	game = chess.pgn.Game()
	game.headers["Event"] = DEFAULT_EVENT
	game.headers["Site"] = DEFAULT_SITE
	game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
	game.headers["Round"] = DEFAULT_ROUND
	game.headers["White"] = DEFAULT_WHITE_SURENAME+", "+DEFAULT_WHITE_FIRSTNAME
	game.headers["Black"] = DEFAULT_BLACK_SURENAME+", "+DEFAULT_BLACK_FIRSTNAME
	game.headers["Result"] = "*"
	node = game
	return game, node
def AddingPGNTAGS(game):
	print("Set this game PGN Tags.\nJust press enter to accept the default value.")
	e="Event: Having fun with Easyfish? "
	event = dgt(prompt=e,kind="s",smax=128,default=DEFAULT_EVENT)
	s="Site: "+os.getenv('COMPUTERNAME')+"'s PC? "
	site = dgt(prompt=s,kind="s",smax=128,default=DEFAULT_SITE)
	round_number = dgt("Enter round number: default= - ",kind="s",smin=1,smax=5,default=DEFAULT_ROUND)
	w1=dgt(prompt="White player's surename? ",kind="s",smin=2,smax=64,default=DEFAULT_WHITE_SURENAME).title()
	w2=dgt(prompt="White player's first name? ",kind="s",smin=2,smax=64,default=DEFAULT_WHITE_FIRSTNAME).title()
	w3=dgt(prompt="Black player's surename? ",kind="s",smin=2,smax=64,default=DEFAULT_BLACK_SURENAME).title()
	w4=dgt(prompt="Black player's first name? ",kind="s",smin=2,smax=64,default=DEFAULT_BLACK_FIRSTNAME).title()
	white_player = f"{w1}, {w2}"
	black_player = f"{w3}, {w4}"
	result_prompt="Choose result: W for White, B for Black, D for draw and U for unknown."
	print(result_prompt)
	while True:
		select_result=key().lower()
		if select_result in "wbdu": break
		else: print(result_prompt)
	if select_result=="w": result="1-0"
	elif select_result=="b": result="0-1"
	elif select_result=="d": result="1/2-1/2"
	elif select_result=="u": result="*"
	game.headers["Event"] = event
	game.headers["Site"] = site
	game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
	game.headers["Round"] = round_number
	game.headers["White"] = white_player
	game.headers["Black"] = black_player
	game.headers["Result"] = result
	return
def LoadGamesFromPGN(PGN_PATH_FILE):
	games = []
	if not os.path.exists(PGN_PATH_FILE):
		with open(PGN_PATH_FILE, "w", encoding="utf-8") as f:
			pass
	else:
		with open(PGN_PATH_FILE, "r", encoding="utf-8") as pgn_file:
			while True:
				game = chess.pgn.read_game(pgn_file)
				if game is None:
					break
				games.append(game)
	return games
def SaveGamesToPGN(file_path, games):
	with open(file_path, "w",encoding="utf-8") as pgn_file:
		for i, game in enumerate(games):
			exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
			game.accept(exporter)
			pgn_file.write(str(exporter))
			if i < len(games) - 1:
				pgn_file.write("\n\n")
	return
def AppendGameToPGN(file_path, new_game):
	if board.fen() == chess.STARTING_FEN and len(board.move_stack)==0:
		print("No game to save")
		return
	games = LoadGamesFromPGN(file_path)
	games.append(new_game)
	SaveGamesToPGN(file_path, games)
	return
def ShowStats(info):
	wdl = info["wdl"]
	depth = info["depth"]
	seldepth = info["seldepth"]
	nps = info["nps"]
	pv = info["pv"]
	hashfull = info["hashfull"]
	if "string" in info.keys():
		debug_string = info["string"]
	else: debug_string="N/A"
	tbhits = info["tbhits"]
	time = info["time"]
	print(f"Results: time {time}, Hash {hashfull}, TB {tbhits}, Dibug: {debug_string}")
	print(f"Depth {depth}/{seldepth}, best {board.san(info['pv'][0])}, score {info['score'].white().score(mate_score=10000)/100:+.2f}, WDL: {wdl[0]/10:.1f}%/{wdl[1]/10:.1f}%/{wdl[2]/10:.1f}%, node {info['nodes']}, NPS {nps}")
	temp_board = board.copy()
	san_moves = ''
	for move in pv:
		san_move = temp_board.san(move)
		san_moves += san_move+" "
		temp_board.push(move)
	print("Line:", san_moves)
	return
def DisambiguateMove(board, move):
	piece = board.piece_at(move.from_square)
	if not piece:
		return ""
	disambiguation = ""
	for other_move in board.legal_moves:
		if other_move != move and other_move.to_square == move.to_square:
			other_piece = board.piece_at(other_move.from_square)
			if other_piece and other_piece.piece_type == piece.piece_type:
				if chess.square_file(other_move.from_square) == chess.square_file(move.from_square):
					disambiguation = str(chess.square_rank(move.from_square) + 1)
				elif chess.square_rank(other_move.from_square) == chess.square_rank(move.from_square):
					disambiguation = COLUMN_TO_NATO[chess.FILE_NAMES[chess.square_file(move.from_square)]]
				else:
					disambiguation = COLUMN_TO_NATO[chess.FILE_NAMES[chess.square_file(move.from_square)]] + " " + str(chess.square_rank(move.from_square) + 1)
				break
	return disambiguation
def MoveToString(board, move):
	piece = board.piece_at(move.from_square)
	if piece is None:
		return "Invalid move"
	to_file = chess.square_file(move.to_square)
	to_rank = chess.square_rank(move.to_square)
	to_nato = COLUMN_TO_NATO[chess.FILE_NAMES[to_file]]
	to_square = f"{to_nato} {to_rank + 1}"
	capture = board.is_capture(move)
	capture_text = ""
	if capture:
		captured_piece = board.piece_at(move.to_square)
		if captured_piece:
			capture_text = f"captures {CHESSPIECE_TO_NAME[captured_piece.piece_type]} on "
		else:
			capture_text = "captures on "  # en passant
	promotion_text = ""
	if move.promotion:
		promotion_text = f", promotes to {CHESSPIECE_TO_NAME[move.promotion]}"
	if board.is_castling(move):
		if move.to_square > move.from_square:
			return "Kingside castling"
		else:
			return "Queenside castling"
	board.push(move)
	check_text = ""
	if board.is_checkmate():
		check_text = ", checkmate"
	elif board.is_check():
		check_text = ", check"
	board.pop()
	disambiguation = DisambiguateMove(board, move)
	move_description = f"{CHESSPIECE_TO_NAME[piece.piece_type]} {disambiguation} to {to_square}"
	if capture_text:
		move_description = f"{CHESSPIECE_TO_NAME[piece.piece_type]} {disambiguation} {capture_text}{to_square}"
	if promotion_text:
		move_description += promotion_text
	move_description += check_text
	return move_description
def GetEngineSet():
	if os.path.isfile(CONFIG_FILE):
		with open(CONFIG_FILE, "r",encoding="utf-8") as f:
			config = json.load(f)
			path = config.get("path")
			filename = config.get("filename")
			engine_path = os.path.join(path, filename)
			if os.path.isfile(engine_path):
				return engine_path, config
			else:
				print("The file specified in the configuration does not exist.")
	print("Hi, I'm Easyfish. I didn't find your configuration file, so I have some questions for you.\nReady? Let's begin.\n")
	path = dgt(prompt="Give me the path location where your UCI engine is saved: ",kind="s",smin=3,smax=256)
	filename = dgt(prompt="Now tell me the exact name of the UCI engine's executable (like, stockfish_15_x64_popcnt.exe): ",kind="s",smin=5,smax=64)
	engine_path = os.path.join(path, filename)
	if os.path.isfile(engine_path):
		# UCI parameters configuration
		hash_size = dgt(prompt="Enter the size of the hash table (min: 1, max: 4096 MB): ",kind="i",imin=1,imax=4096)
		max_cores = multiprocessing.cpu_count()
		num_cores = dgt(prompt=f"Enter the number of cores to use (min: 1, max: {max_cores}): ",kind="i",imin=1,imax=max_cores,default=4)
		skill_level = dgt(prompt="Enter the skill level (min: 0, max: 20): ",kind="i",imin=0,imax=20)
		move_overhead = dgt(prompt="Enter the move overhead in milliseconds (min: 0, max: 500): ",kind="i",imin=0,imax=500,default=0)
		wdl_switch=True
		# Other parameters can be added here
		config = {
			"path": path,
			"filename": filename,
			"hash_size": hash_size,
			"num_cores": num_cores,
			"skill_level": skill_level,
			"move_overhead": move_overhead,
			"wdl_switch": wdl_switch}
			# Add other parameters if needed
		with open(CONFIG_FILE, "w",encoding="utf-8") as f:
			json.dump(config, f)
		return engine_path, config
	else:
		print("The specified file does not exist. Check the path and executable name.")
		return None, None
def CalculateMaterial(board):
	white_value = 0
	black_value = 0
	for square in chess.SQUARES:
		piece = board.piece_at(square)
		if piece is not None:
			piece_symbol = piece.symbol()
			if piece_symbol.isupper():
				white_value += PIECE_VALUES[piece_symbol]
			else:
				black_value += PIECE_VALUES[piece_symbol]
	return white_value, black_value
def InsertedCounter(l):
	p=''; p1= '';white_material=0;black_material=0
	for j in l:
		if l.count(j)>0:
			if j not in p: p+=f"{j}-{l.count(j)}, "
	white_material,black_material=CalculateMaterial(board)
	p1=f"[{white_material}/{black_material}]: {p}> "
	return p1
def SquaresListToString(l, report_piece=False, occupied_only=False):
	result=""
	for j in l:
		is_piece = board.piece_at(chess.parse_square(j))
		if is_piece:
			color = 'White' if is_piece.color == chess.WHITE else 'Black'
			if report_piece:
				result += f"{color} {CHESSPIECE_TO_NAME[is_piece.piece_type]} on {COLUMN_TO_NATO[j[0]]} {j[1]}, "
			elif not occupied_only:
				result += f"{COLUMN_TO_NATO[j[0]]} {j[1]}, "
		elif not occupied_only:
			result += f"{COLUMN_TO_NATO[j[0]]} {j[1]}, "
	if result == "":
		result = "None."
	else:
		result = result[:-2] + "."
	return result
def ExploreColumnsOrRows(index, vertical=True):
	squares = []
	if board.turn: s1,s2,s3=0,8,1
	else: s1,s2,s3=7,-1,-1
	if vertical:
		for row in range(s1,s2,s3):
			square = chess.square(index, row)
			squares.append(chess.square_name(square))
	else:
		for col in range(s1,s2,s3):
			square = chess.square(col, index)
			squares.append(chess.square_name(square))
	return squares
def GetPiecesPosition(board, piece_type):
	if piece_type not in SAN_CHESSPIECES:
		return []
	piece_code = SAN_CHESSPIECES[piece_type]
	piece_color = chess.WHITE if piece_type.isupper() else chess.BLACK
	positions = [square for square in chess.SQUARES if board.piece_at(square) == chess.Piece(piece_code, piece_color)]
	positions_algebraic = [chess.square_name(pos) for pos in positions]
	return positions_algebraic
def BoardEditor():
	print("\nBoard Editor. Setting up a new position by placing pieces over the board.\nPlease enter piece and square like Ng1. Type 'ok' when you're done; type Xf2 to remove a piece.")
	tmp_board=CustomBoard()
	tmp_board.clear()
	prompt="PieceSquare (e.g. Kc4)> "
	inserted_pieces=[]
	while True:
		while True:
			wherewho=dgt(prompt=prompt,kind="s",smin=2,smax=3)
			if wherewho=="ok": break
			square=wherewho[-2:]; piece_name = wherewho[0]
			square=square.lower()
			if square[0] in 'abcdefgh' and square[1] in '12345678' and piece_name in 'RrBbNnKkQqPpXx': break
			else: print("It is not a valid square or piece kind")
		if wherewho=="done" and tmp_board.is_valid(): break
		position = chess.parse_square(square)
		piece = None
		if piece_name.lower() == 'p':
			piece = chess.Piece(chess.PAWN, chess.WHITE if piece_name.isupper() else chess.BLACK)
		elif piece_name.lower() == 'n':
			piece = chess.Piece(chess.KNIGHT, chess.WHITE if piece_name.isupper() else chess.BLACK)
		elif piece_name.lower() == 'b':
			piece = chess.Piece(chess.BISHOP, chess.WHITE if piece_name.isupper() else chess.BLACK)
		elif piece_name.lower() == 'r':
			piece = chess.Piece(chess.ROOK, chess.WHITE if piece_name.isupper() else chess.BLACK)
		elif piece_name.lower() == 'q':
			piece = chess.Piece(chess.QUEEN, chess.WHITE if piece_name.isupper() else chess.BLACK)
		elif piece_name.lower() == 'k':
			piece = chess.Piece(chess.KING, chess.WHITE if piece_name.isupper() else chess.BLACK)
		if piece_name in "Xx":
			tmp_board.remove_piece_at(position)
		else: tmp_board.set_piece_at(position, piece)
		if not tmp_board.is_valid(): print("Position still illegal.")
		inserted_pieces.append(piece_name)
		prompt = InsertedCounter(inserted_pieces)
	print("Now tell me if it's white's turn (W) or black's (B)? ")
	while True:
		color_turn = key(attesa=45).lower()
		if color_turn in "bw": break
		else: print("Please choose W for White or B for Black")
	if color_turn == "w": tmp_board.turn = chess.WHITE
	else: tmp_board.turn = chess.BLACK
	any_en_passant=dgt(prompt="is there en_passant? If so enter the square, otherwise just hit enter:",kind="s",smax=2)
	if any_en_passant!="":
		if any_en_passant[0] in "ABCDEFGH" and any_en_passant[1] in "12345678":
			tmp_board.set_ep_square(chess.parse_square(any_en_passant[:2]))
			print("Set")
	print("Let me know what about castling rights.")
	castling_rights = 0
	questions = [
		("White kingside castling (O-O)", chess.BB_H1),
		("White queenside castling (O-O-O)", chess.BB_A1),
		("Black kingside castling (O-O)", chess.BB_H8),
		("Black queenside castling (O-O-O)", chess.BB_A8)]
	for question, bb in questions:
		response = key(prompt=f"{question}? (y/n): ").strip().lower()
		if response == 'y':
			castling_rights |= bb
	tmp_board.castling_rights = castling_rights
	print("Set")
	tmp_board.fullmove_number = dgt(prompt="Moves starting from, 1? ",kind="i",imin=1,imax=250,default=1)
	tmp_board.halfmove_clock = dgt(prompt="Half move clock counting from, 0? ",kind="i",imin=0,imax=250,default=0)
	print("Set\n"+tmp_board)
	return tmp_board.fen()
def InfoSquare(board, square):
	piece = board.piece_at(square)
	if piece:
		piece_info = SYMBOLS_TO_NAME[piece.symbol()]
	else: piece_info="no piece"
	attacked_by_white = board.is_attacked_by(chess.WHITE, square)
	attacked_by_black = board.is_attacked_by(chess.BLACK, square)
	defended_by_white = any(board.is_attacked_by(chess.WHITE, s) for s in board.attackers(chess.WHITE, square))
	defended_by_black = any(board.is_attacked_by(chess.BLACK, s) for s in board.attackers(chess.BLACK, square))
	square_color = "Dark" if (chess.square_rank(square) + chess.square_file(square)) % 2 == 0 else "Light"
	attacked_info = "white and black" if attacked_by_white and attacked_by_black else "white" if attacked_by_white else "black" if attacked_by_black else "none"
	defended_info = "white and black" if defended_by_white and defended_by_black else "white" if defended_by_white else "black" if defended_by_black else "none"
	info_string = f"{square_color} {chess.square_name(square)} square contains {piece_info}, it is attacked by {attacked_info}, it is defended by {defended_info}."
	return info_string
def GetPieceMoves(piece_symbol, square_str, legal_moves=True, occupied_only_square=True):
	tmp_board = board.copy()
	square = chess.parse_square(square_str)
	tmp_board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))
	if legal_moves:
		moves = tmp_board.legal_moves
	else:
		tmp_board.clear()
		tmp_board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))
		moves = tmp_board.generate_pseudo_legal_moves()
	piece_moves = [move for move in moves if move.from_square == square]
	piece_moves_squares = [move.uci()[2:] for move in piece_moves]
	result = []
	for dest_square_str in piece_moves_squares:
		dest_square = chess.parse_square(dest_square_str)
		piece_at_dest = board.piece_at(dest_square)
		if occupied_only_square:
			if piece_at_dest:
				piece_color = "White" if piece_at_dest.color == chess.WHITE else "Black"
				piece_type = piece_at_dest.symbol().lower() if piece_at_dest.color == chess.BLACK else piece_at_dest.symbol()
				piece_type_full = chess.piece_name(piece_at_dest.piece_type)
				piece_info = f"{piece_color} {piece_type_full} on {COLUMN_TO_NATO[dest_square_str[0]]} {dest_square_str[1]}"
				result.append(piece_info)
		else:
			if piece_at_dest:
				piece_color = "White" if piece_at_dest.color == chess.WHITE else "Black"
				piece_type = piece_at_dest.symbol().lower() if piece_at_dest.color == chess.BLACK else piece_at_dest.symbol()
				piece_type_full = chess.piece_name(piece_at_dest.piece_type)
				piece_info = f"{piece_color} {piece_type_full} on {COLUMN_TO_NATO[dest_square_str[0]]} {dest_square_str[1]}"
			else:
				piece_info = f"{COLUMN_TO_NATO[dest_square_str[0]]} {dest_square_str[1]}"
			result.append(piece_info)
	s = ', '.join(result)
	result = ''
	current_line = ''
	words = s.split(' ')
	for word in words:
		if len(current_line) + len(word) + 1 > 75:
			result += current_line.strip() + '\n'
			current_line = word + ' '
		else:
			current_line += word + ' '
	result += current_line.strip()
	return result
def ExplorerMode(game, engine):
	node = game
	initial_board = CustomBoard()
	global analysis_time
	def SyncBoardToNode(node):
		board = initial_board.copy()
		move_stack = []
		while node.parent:
			move_stack.append(node.move)
			node = node.parent
		move_stack.reverse()
		for move in move_stack:
			if move:
				board.push(move)
		return board
	def GetPrincipalVariationSan(board, pv):
		temp_board = board.copy()
		san_moves = []
		for move in pv:
			san_moves.append(temp_board.san(move))
			temp_board.push(move)
		return san_moves
	current_board = SyncBoardToNode(node)
	while True:
		if node.parent:
			parent_move = node.parent.san() if node.parent.move else None
		else:
			parent_move = None
		if node.move:
			current_move = node.san()
		else:
			current_move = "start"
		if node.variations:
			next_move = node.variations[0].san()
			variant_count = len(node.variations)
		else:
			next_move = game.headers.get("Result", "end")
			variant_count = 0
		if node.comment:
			print(node.comment)
		level = 0
		temp_node = node
		while temp_node.parent:
			if len(temp_node.parent.variations) > 1:
				level += 1
			temp_node = temp_node.parent
		level_prefix = f"Lvl{level}" if level > 0 else "Mainline"
		prompt = f"\n[{level_prefix}] {parent_move or ''} ({current_move}) {next_move}"
		if variant_count > 1:
			prompt += f" V{variant_count}"
		command = key(prompt=prompt)
		if command == 'a':
			if node.parent:
				node = node.parent
				current_board = SyncBoardToNode(node)
			else:
				print("No previous move")
		elif command == '?': menu(d=MNEXPLORER,show=True)
		elif command == 'd':
			if node.variations:
				if variant_count > 1:
					while True:
						var_index = 0
						while True:
							var_prompt = f"\nVariant {var_index+1}/{variant_count}: {node.variations[var_index].san()}"
							var_command = key(prompt=var_prompt)
							if var_command == 'x' and var_index < variant_count - 1:
								var_index += 1
							elif var_command == 'w' and var_index > 0:
								var_index -= 1
							elif var_command == 'd':
								node = node.variations[var_index]
								current_board.push(node.move)
								break
							elif var_command == chr(27):  # ESC key
								return
						break
				else:
					node = node.variations[0]
					current_board.push(node.move)
			else:
				print("end of the game")
		elif command == 'q':
			node = game
			current_board = SyncBoardToNode(node)  # Ripristina la scacchiera iniziale
		elif command == 'e':
			while node.variations:
				node = node.variations[0]
				current_board.push(node.move)  # Applica la mossa per aggiornare la posizione
		elif command == 'z':
			while node.parent and node.parent.variations[0] != node:
				node = node.parent
				current_board = SyncBoardToNode(node)
			if node.parent:
				node = node.parent
				current_board = SyncBoardToNode(node)
		elif command == 'c':
			if node.comment:
				print(node.comment)
		elif command == 's':
			current_board = SyncBoardToNode(node)
			print("Analyzing...")
			analysis = engine.analyse(current_board, chess.engine.Limit(time=analysis_time))
			best_move_san = current_board.san(analysis['pv'][0])
			principal_variation_san = ' '.join(GetPrincipalVariationSan(current_board, analysis['pv']))
			print("\nBest move:", best_move_san)
			print("Best line:", principal_variation_san)
		elif command == 'r':
			new_time = dgt(prompt="Enter analysis time in seconds: ", kind="i", imin=1,imax=1800)
			analysis_time = new_time
		elif command == chr(27):
			print()
			return
engine_path, config = GetEngineSet()
if engine_path:
	engine = chess.engine.SimpleEngine.popen_uci(engine_path)
	engine.configure({"Hash": config["hash_size"]})
	engine.configure({"Threads": config["num_cores"]})
	engine.configure({"Skill Level": config["skill_level"]})
	engine.configure({"Move Overhead": config["move_overhead"]})
	engine.configure({"UCI_ShowWDL": config["wdl_switch"]})
	# Configure other parameters if needed

#QV
analysis_time = 2
info, pv, multipv = {}, '', 3
fen_from_clip=""
board = CustomBoard()
existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
print(f"Loaded {len(existing_games)} existing games in PGN database.")
game, node = NewGame()
prompt="MOVE 1.: "

#QMain
print(f"Hi, it's Easyfish {VER}, here, by Gabriele Battaglia (IZ4APU).\n\tI'm ready to help you. Enjoy!")

while True:
	key_command=dgt(prompt=prompt, kind="s", smin=1, smax=8192)
	number_command = ''.join([char for char in key_command if char.isdigit()])
	if number_command != "":
		number_command=int(number_command)
		if number_command<1: number_command=1
		elif number_command>600: number_command=600
	if key_command[0] == ".":
		key_command=key_command.lower()
		if key_command == ".q": break
		elif key_command==".e":
			print("Entering Explorer mode...")
			ExplorerMode(game, engine)
		elif key_command==".b": print(board)
		elif key_command==".bm":
			white, black = CalculateMaterial(board)
			print(f"Material on the board: {white}/{black} White/Black")
		elif key_command==".pt": AddingPGNTAGS(game)
		elif key_command==".gp":
			if pyperclip.paste() == "":
				print("Sorry, your clipboard is empty. Please copy a valid PGN first.") 
			AppendGameToPGN(PGN_FILE_PATH, game)
			print("Paste a new position from FEN in your system clipboard.\n\tChecking FEN...")
			try:
				tmp_board = board.copy()
				tmp_board.set_fen(fen_from_clip)
				print("FEN is ok.")
				board = tmp_board.copy()
				game, node = NewGame()
				game = PastePGNFromClipboard()
				if game:
					print("Game loaded succesfully")
				del tmp_board
				prompt="START 1.: "
				print(board)
			except ValueError:
				print("Invalid PGN in the clipboard.")
		elif key_command==".gp":
			CopyPGNToClipboard(game)
		elif key_command==".gf":
			pyperclip.copy(board.fen())
			print("Game to FEN. Copied to the clipboard")
		elif key_command==".n":
			print("Set up a new board from scratch. You're ready to go!")
			AppendGameToPGN(PGN_FILE_PATH, game)
			print("Old game saved.")
			existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
			print(f"Loaded {len(existing_games)} existing games in PGN database.")
			game, node = NewGame()
			board = CustomBoard()
			prompt="START 1.: "
		elif key_command==".be":
			AppendGameToPGN(PGN_FILE_PATH, game)
			existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
			game, node = NewGame()
			board = CustomBoard()
			fen = BoardEditor()
			board.set_fen(fen)
			prompt="START 1.: "
		elif key_command==".fg":
			fen_from_clip = pyperclip.paste()
			if fen_from_clip == "":
				print("Sorry, your clipboard is empty. Please copy a valid FEN first.") 
			else:
				print("Paste a new position from FEN in your system clipboard.\n\tChecking FEN...")
				try:
					tmp_board = board.copy()
					tmp_board.set_fen(fen_from_clip)
					print("FEN is ok.")
					AppendGameToPGN(PGN_FILE_PATH, game)
					print("Current game saved.")
					existing_games = LoadGamesFromPGN(PGN_FILE_PATH)
					print(f"Loaded {len(existing_games)} existing games in PGN database.")
					board = tmp_board.copy()
					game, node = NewGame()
					game.setup(board)
					del tmp_board
					prompt="START 1.: "
					print(board)
				except ValueError:
					print("Invalid FEN string.")
		elif key_command==".ssf": os.startfile(CONFIG_FILE)
		elif key_command==".snl":
			multipv=dgt(prompt=f"Set a new number for analyses lines, now current to {multipv}: ",kind="i",imin=1,imax=256,default=3)
			print(multipv,"set.")
		elif key_command==".?": menu(d=MNMAIN,show=True)
		elif key_command.startswith(".a"):
			if number_command=="": number_command=1
			print(f"Analyzing current position for {number_command} seconds.")
			limit = chess.engine.Limit(time=number_command)
			info = engine.analyse(board, limit, multipv=multipv)
			ShowStats(info[0])
		elif key_command.startswith(".l"):
			if len(info)>0:
				if number_command in ('', 0, 1): number_command=0
				elif number_command>1: number_command-=1
				if multipv>1 and number_command>=multipv:
					print(f"There are only {multipv} analyses line available")
					number_command=multipv-1
				if number_command==0:
					print("Best line:")
					ShowStats(info[number_command])
				else:
					print(f"{number_command+1}° choice:")
					ShowStats(info[number_command])
			else: print("First you must do some analyses by sending .a command")
		elif key_command not in MNMAIN.keys(): print(f"Sorry but {key_command} is not a valid command.\nType 'M' for the menu.")
	elif key_command[0] == ",":
			if key_command[1] in SYMBOLS_TO_NAME.keys():
				algebric=GetPiecesPosition(board, key_command[1])
				found=SYMBOLS_TO_NAME[key_command[1]]
				found+=": "+SquaresListToString(algebric)
				print(found)
			else: print(key_command[1], "is not a valid piece name")
	elif key_command[0] == "-":
		if len(key_command)==3:
			square=key_command[-2:].lower()
			if square[0] in "abcdefgh" and square [1] in "12345678":
				print(InfoSquare(board, chess.parse_square(square)))
			else: print("Not a valid square")
		elif len(key_command)==2:
			if key_command[1] in "abcdefgh":
				found_occupied_square=SquaresListToString(ExploreColumnsOrRows(ord(key_command[1])-97,vertical=True),True,True)
				print(f"Pieces on column {COLUMN_TO_NATO[key_command[1]]} are: {found_occupied_square}")
			elif key_command[1] in "12345678":
				found_occupied_square=SquaresListToString(ExploreColumnsOrRows(int(key_command[1])-1,vertical=False),True,True)
				print(f"Pieces on row {key_command[1]} are: {found_occupied_square}")
		elif len(key_command)==4:
			square=key_command[-2:].lower()
			piece=key_command[1].upper()
			if square[0] in "abcdefgh" and square [1] in "12345678" and piece in SYMBOLS_TO_NAME.keys():
				if board.piece_at(chess.parse_square(square)):
					lm=False; oos=False
				else: lm=True; oos=False
				legal_move_str = GetPieceMoves(piece, square, legal_moves=lm, occupied_only_square=oos)
				print(f"{SYMBOLS_TO_NAME[piece][6:].capitalize()}'s moves from {COLUMN_TO_NATO[square[0]]} {square[1]} are: {legal_move_str}")
			else: print("Piece's name or square not valid")
		else: print("not a valid exploration command")
	elif key_command[0] == "_":
		node.comment = key_command[1:]
		print("Comment recorded.")
	else:
			if key_command in ('o-o', 'oo', '00'): key_command="O-O"
			elif key_command in ('o-o-o', 'ooo', '000'): key_command="O-O-O"
			elif key_command[0] in "rnqk": key_command=key_command[0].upper()+key_command[1:]
			try:
				move=board.parse_san(key_command)
				print(MoveToString(board, move))
				board.push(move)
				node = node.add_main_variation(move)
				prompt=f"{board.fullmove_number}... {board.san_and_push(board.pop())}: " if board.turn else f"{board.fullmove_number}. {board.san_and_push(board.pop())}: "
			except ValueError:
				print(f"{key_command}: illegal move.")

AppendGameToPGN(PGN_FILE_PATH, game)
updated_games = LoadGamesFromPGN(PGN_FILE_PATH)
print(f"{len(updated_games)} games in PGN database at {PGN_FILE_PATH}.\n\tBye-Bye from Easyfish version {VER}, by Gabriele Battaglia (IZ4APU)\n\tsee you soon!")
engine.quit()