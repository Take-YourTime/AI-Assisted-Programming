import curses

# Initialize curses screen and set up color support.
curses.initscr()
curses.start_color()

# Board constants
BOARD_SIZE = 8
EMPTY = " "
CURSOR_COLORS = {
    "blue": curses.color_pair(1),
    "green": curses.color_pair(2),
    "yellow": curses.color_pair(3),
}
BORDER_COLOR = curses.color_pair(6) # Color for the board border.


WHITE_PIECES = {"R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙"}
BLACK_PIECES = {"R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟"}

initial_board = [
    ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
    ["♟"] * BOARD_SIZE,
    [EMPTY] * BOARD_SIZE,
    [EMPTY] * BOARD_SIZE,
    [EMPTY] * BOARD_SIZE,
    [EMPTY] * BOARD_SIZE,
    ["♙"] * BOARD_SIZE,
    ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"]
]

def init_colors() -> None:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_YELLOW)

def draw_board(stdscr, board, cursor_pos, cursor_color, valid_moves=[]) -> None:
    stdscr.clear()  # Clear screen for redraw.
    height, width = stdscr.getmaxyx()  # Get terminal dimensions.
    
    # Check if terminal size can display the board.
    if height < BOARD_SIZE + 2 or width < BOARD_SIZE * 2 + 4:
        stdscr.addstr(0, 0, "Terminal too small for board display. Please enlarge the window.", curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()
        return
    
    # Draw the border around the chessboard.
    for y in range(-1, BOARD_SIZE + 1):
        for x in range(-1, BOARD_SIZE + 1):
            if y == -1 or y == BOARD_SIZE or x == -1 or x == BOARD_SIZE:
                stdscr.addstr(y + 1, x * 2 + 2, "  ", BORDER_COLOR)

    # Draw each piece on the board.
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            piece = board[y][x]  # Get the piece at the current position.
            # Determine color based on cursor position, valid moves, or board square.
            if (y, x) == cursor_pos:
                color = cursor_color
            elif (y, x) in valid_moves:
                color = CURSOR_COLORS["green"]
            else:
                color = curses.color_pair(4) if (y + x) % 2 else curses.color_pair(5)
            # Display the piece or empty cell.
            stdscr.addstr(y + 1, x * 2 + 2, f"{piece} ", color)
    stdscr.refresh()  # Refresh to show updates.
    curses.curs_set(0) # Hides the cursor for UI cleanliness.


# Calculates valid moves for a selected piece based on its type.
def get_valid_moves(piece, position, board) -> list:
    y, x = position  # Current coordinates of the piece.
    moves = []       # List of valid moves for the piece.
    is_white = piece in WHITE_PIECES.values()
    direction = -1 if is_white else 1  # Movement direction: -1 for white (up), 1 for black (down).

    # Define movement rules for each piece type.
    if piece in ["♙", "♟"]:  # Pawn
        # Forward movement (1 square).
        if 0 <= y + direction < BOARD_SIZE and board[y + direction][x] == EMPTY:
            moves.append((y + direction, x))
            
            # First move: Can move 2 squares if both are empty.
            start_row = 6 if is_white else 1
            if y == start_row and board[y + direction * 2][x] == EMPTY:
                moves.append((y + direction * 2, x))
        
        # Diagonal capture.
        for dx in [-1, 1]:  # Left and right diagonal.
            ny, nx = y + direction, x + dx
            if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                target = board[ny][nx]
                if target != EMPTY and (
                    (is_white and target in BLACK_PIECES.values()) or
                    (not is_white and target in WHITE_PIECES.values())
                ):
                    moves.append((ny, nx))
    
    elif piece in ["♖", "♜"]:  # Rook
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y, x
            while 0 <= ny + dy < BOARD_SIZE and 0 <= nx + dx < BOARD_SIZE:
                ny += dy
                nx += dx
                target = board[ny][nx]
                if target != EMPTY:
                    if (is_white and target in BLACK_PIECES.values()) or \
                       (not is_white and target in WHITE_PIECES.values()):
                        moves.append((ny, nx))  # Capture opponent piece.
                    break  # Stop at the first non-empty square.
                moves.append((ny, nx))  # Empty square.

    elif piece in ["♘", "♞"]:  # Knight
        for dy, dx in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                target = board[ny][nx]
                if target == EMPTY or (is_white and target in BLACK_PIECES.values()) or \
                   (not is_white and target in WHITE_PIECES.values()):
                    moves.append((ny, nx))

    elif piece in ["♗", "♝"]:  # Bishop
        for dy, dx in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ny, nx = y, x
            while 0 <= ny + dy < BOARD_SIZE and 0 <= nx + dx < BOARD_SIZE:
                ny += dy
                nx += dx
                target = board[ny][nx]
                if target != EMPTY:
                    if (is_white and target in BLACK_PIECES.values()) or \
                       (not is_white and target in WHITE_PIECES.values()):
                        moves.append((ny, nx))  # Capture opponent piece.
                    break
                moves.append((ny, nx))  # Empty square.

    elif piece in ["♕", "♛"]:  # Queen
        # Combine rook and bishop moves.
        moves.extend(get_valid_moves("♖", position, board))
        moves.extend(get_valid_moves("♗", position, board))

    elif piece in ["♔", "♚"]:  # King
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                target = board[ny][nx]
                if target == EMPTY or (is_white and target in BLACK_PIECES.values()) or \
                   (not is_white and target in WHITE_PIECES.values()):
                    moves.append((ny, nx))

    return moves  # Return the list of valid moves.

