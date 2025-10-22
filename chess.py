"""
Simple Console Chess in Python
- Legal moves, check/checkmate/stalemate detection
- Pawn promotions auto-queen
- No castling or en passant (can be added later)
- Text UI with algebraic coordinates (e.g., "e2 e4")

Run:
  python console_chess.py
Commands inside the game:
  e2 e4        # make a move
  moves e2     # list legal moves from e2 on your turn
  quit         # exit
"""
from typing import List, Tuple, Optional

WHITE, BLACK = 'w', 'b'
Piece = Tuple[str, str]  # (color, type)

# Board is List[List[Optional[Piece]]] with (row 0 at 8th rank)
def initial_board() -> List[List[Optional[Piece]]]:
    back = ['r','n','b','q','k','b','n','r']
    board: List[List[Optional[Piece]]] = []
    board.append([(BLACK, p) for p in back])
    board.append([(BLACK, 'p') for _ in range(8)])
    for _ in range(4):
        board.append([None for _ in range(8)])
    board.append([(WHITE, 'p') for _ in range(8)])
    board.append([(WHITE, p) for p in back])
    return board

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8

def find_king(board, color):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p[0] == color and p[1] == 'k':
                return (r, c)
    return None

def algebraic_to_rc(s: str) -> Tuple[int, int]:
    file = ord(s[0].lower()) - ord('a')
    rank = int(s[1]) - 1
    return (7 - rank, file)  # row 0 is rank 8

def rc_to_algebraic(r: int, c: int) -> str:
    file = chr(c + ord('a'))
    rank = str(8 - r)
    return file + rank

def copy_board(board):
    return [row.copy() for row in board]

def is_square_attacked(board, r, c, by_color) -> bool:
    # Pawn attacks
    dir = -1 if by_color == WHITE else 1
    for dc in (-1, 1):
        rr = r - dir
        cc = c + dc
        if in_bounds(rr, cc):
            p = board[rr][cc]
            if p and p[0] == by_color and p[1] == 'p':
                return True
    # Knights
    for dr, dc in [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc):
            p = board[rr][cc]
            if p and p[0] == by_color and p[1] == 'n':
                return True
    # Bishops/Queens diagonals
    for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            p = board[rr][cc]
            if p:
                if p[0] == by_color and (p[1] == 'b' or p[1] == 'q'):
                    return True
                break
            rr += dr; cc += dc
    # Rooks/Queens orthogonal
    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            p = board[rr][cc]
            if p:
                if p[0] == by_color and (p[1] == 'r' or p[1] == 'q'):
                    return True
                break
            rr += dr; cc += dc
    # King
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0: 
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                p = board[rr][cc]
                if p and p[0] == by_color and p[1] == 'k':
                    return True
    return False

def legal_moves_from(board, r, c, color, last_move=None):
    p = board[r][c]
    if not p or p[0] != color:
        return []
    typ = p[1]
    moves = []

    def add_move(rr, cc):
        # simulate to avoid self-check
        b2 = copy_board(board)
        b2[rr][cc] = b2[r][c]
        b2[r][c] = None
        kr, kc = find_king(b2, color)
        enemy = WHITE if color == BLACK else BLACK
        if not is_square_attacked(b2, kr, kc, enemy):
            moves.append((rr, cc))

    if typ == 'p':
        dir = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        # single push
        rr, cc = r + dir, c
        if in_bounds(rr, cc) and board[rr][cc] is None:
            add_move(rr, cc)
            # double push
            rr2 = r + 2 * dir
            if r == start_row and board[rr2][cc] is None:
                add_move(rr2, cc)
        # captures
        for dc in (-1, 1):
            rr, cc = r + dir, c + dc
            if in_bounds(rr, cc) and board[rr][cc] and board[rr][cc][0] != color:
                add_move(rr, cc)
        # (no en passant here)
    elif typ == 'n':
        for dr, dc in [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and (board[rr][cc] is None or board[rr][cc][0] != color):
                add_move(rr, cc)
    elif typ in ('b', 'r', 'q'):
        dirs = []
        if typ in ('b', 'q'):
            dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
        if typ in ('r', 'q'):
            dirs += [(1,0),(-1,0),(0,1),(0,-1)]
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while in_bounds(rr, cc):
                if board[rr][cc] is None:
                    add_move(rr, cc)
                else:
                    if board[rr][cc][0] != color:
                        add_move(rr, cc)
                    break
                rr += dr; cc += dc
    elif typ == 'k':
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc) and (board[rr][cc] is None or board[rr][cc][0] != color):
                    add_move(rr, cc)
        # (no castling here)
    return moves

def all_legal_moves(board, color):
    res = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p[0] == color:
                ms = legal_moves_from(board, r, c, color)
                for rr, cc in ms:
                    res.append(((r, c), (rr, cc)))
    return res

def move(board, src, dst, color) -> Tuple[bool, str]:
    r1, c1 = algebraic_to_rc(src)
    r2, c2 = algebraic_to_rc(dst)
    if not in_bounds(r1, c1) or not in_bounds(r2, c2):
        return False, "Out of bounds."
    p = board[r1][c1]
    if not p or p[0] != color:
        return False, "No piece of yours on source."
    ms = legal_moves_from(board, r1, c1, color)
    if (r2, c2) not in ms:
        return False, "Illegal move."
    piece = board[r1][c1]
    board[r1][c1] = None
    # auto-queen promotion
    if piece[1] == 'p' and (r2 == 0 or r2 == 7):
        board[r2][c2] = (color, 'q')
    else:
        board[r2][c2] = piece
    return True, "OK"

def in_check(board, color) -> bool:
    kr, kc = find_king(board, color)
    enemy = WHITE if color == BLACK else BLACK
    return is_square_attacked(board, kr, kc, enemy)

def is_checkmate(board, color) -> bool:
    if not in_check(board, color):
        return False
    return len(all_legal_moves(board, color)) == 0

def is_stalemate(board, color) -> bool:
    if in_check(board, color):
        return False
    return len(all_legal_moves(board, color)) == 0

def board_str(board) -> str:
    s = "  +-----------------+\n"
    for r in range(8):
        s += str(8 - r) + " |"
        for c in range(8):
            p = board[r][c]
            if not p:
                s += " ."
            else:
                ch = p[1].upper() if p[0] == WHITE else p[1]
                s += " " + ch
        s += " |\n"
    s += "  +-----------------+\n"
    s += "    a b c d e f g h\n"
    return s

def main():
    board = initial_board()
    turn = WHITE
    print("Simple Console Chess (no castling/en passant). Enter moves like 'e2 e4'.")
    print("Commands: 'moves e2' to list moves; 'quit' to exit.\n")
    while True:
        print(board_str(board))
        if is_checkmate(board, turn):
            print(("White" if turn == WHITE else "Black"), "is checkmated.",
                  ("Black" if turn == WHITE else "White"), "wins!")
            break
        if is_stalemate(board, turn):
            print("Stalemate. Draw.")
            break
        if in_check(board, turn):
            print(("White" if turn == WHITE else "Black"), "to move — CHECK.")
        else:
            print(("White" if turn == WHITE else "Black"), "to move.")
        cmd = input("> ").strip()
        if cmd.lower() in ("quit", "exit"):
            break
        if cmd.lower().startswith("moves "):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: moves <square>")
                continue
            sq = parts[1]
            try:
                r, c = algebraic_to_rc(sq)
            except Exception:
                print("Bad square.")
                continue
            ms = legal_moves_from(board, r, c, turn)
            if not ms:
                print("No legal moves for", sq)
            else:
                print("Legal moves:", ", ".join(rc_to_algebraic(rr, cc) for rr, cc in ms))
            continue
        parts = cmd.split()
        if len(parts) != 2:
            print("Enter a move like: e2 e4")
            continue
        src, dst = parts
        ok, msg = move(board, src, dst, turn)
        if not ok:
            print("Error:", msg)
            continue
        turn = BLACK if turn == WHITE else WHITE

if __name__ == "__main__":
    main()
