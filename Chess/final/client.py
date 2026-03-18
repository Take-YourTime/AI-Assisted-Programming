import curses
import socket
import pickle
import time
from share import BLACK_PIECES, WHITE_PIECES, init_colors, draw_board, get_valid_moves, initial_board, EMPTY, CURSOR_COLORS

HOST = "192.168.243.145"  # Replace with server's IP.
PORT = 65432            # Port to connect.

def init_network():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print(f"Connected to server {HOST}:{PORT}")
    return sock

def send_data(sock, data):
    sock.sendall(pickle.dumps(data))

def receive_data(sock):
    return pickle.loads(sock.recv(4096))

# black player
def main(stdscr):
    init_colors()   # Initialize color pairs.

    conn = init_network()

    board = [row[:] for row in initial_board]
    cursor_pos = (0, 0)  # Starting cursor position.
    mode = "blue"        # Start in blue mode for selection.
    current_player = "black"
    selected_piece = None
    valid_moves = []     # List of valid moves for the selected piece.
    running =  True

    while running:
        draw_board(stdscr, board, cursor_pos, CURSOR_COLORS[mode], valid_moves)
        stdscr.addstr(len(board) + 2, 0, f"Current turn: {current_player}")

        # Player's turn.
        if current_player == "black":
            key = stdscr.getch()    # Wait for user input.
            y, x = cursor_pos       # Get current cursor position.

            # Handle cursor movement with arrow keys.
            if key == curses.KEY_UP:
                cursor_pos = (max(0, y - 1), x)
            elif key == curses.KEY_DOWN:
                cursor_pos = (min(len(board) - 1, y + 1), x)
            elif key == curses.KEY_LEFT:
                cursor_pos = (y, max(0, x - 1))
            elif key == curses.KEY_RIGHT:
                cursor_pos = (y, min(len(board[0]) - 1, x + 1))
            
            elif key == ord('\n'):  # Enter key to select or move a piece.
                piece = board[y][x]
                if mode == "blue":
                     # Check if player selects their own piece.
                    if piece in BLACK_PIECES.values():
                        selected_piece = (y, x)
                        valid_moves = get_valid_moves(piece, selected_piece, board)
                        mode = "green"
                    else:
                        # Invalid selection warning.
                        mode = "yellow"
                        draw_board(stdscr, board, cursor_pos, CURSOR_COLORS["yellow"])
                        time.sleep(0.2)
                        mode = "blue"
                elif mode == "green":
                    # Move selected piece if the target is valid.
                    if selected_piece and (y, x) in valid_moves:
                        if board[y][x] == "♔": # Check if it eats white king.
                            stdscr.addstr(len(board) + 3, 0, "Black wins!")
                            running = False
                            send_data(conn, {"running": running})
                            
                        sy, sx = selected_piece
                        board[y][x] = board[sy][sx]
                        board[sy][sx] = EMPTY
                        current_player = "white"
                        mode = "blue"
                        selected_piece = None
                        valid_moves = []
                        send_data(conn, {"board": board, "current_player": "white"})
                    else:
                        # Invalid move warning.
                        mode = "yellow"
                        draw_board(stdscr, board, cursor_pos, CURSOR_COLORS["yellow"])
                        time.sleep(0.2)
                        mode = "green"
            elif key == 27: # Esc key to cancel piece selection.
                if mode == "green":
                    mode = "blue"
                    selected_piece = None
                    valid_moves = []
        else:
            # Wait for opponent's move.
            stdscr.addstr(len(board) + 3, 0, "Waiting for opponent's move...")
            stdscr.refresh()
            data = receive_data(conn)
            board = data["board"]
            current_player = data["current_player"]
    


if __name__ == "__main__":
    curses.wrapper(main)
