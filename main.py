import tkinter as tk
import random
import time

# Game configuration
GRID_SIZE = 10   # Grid size (10x10)
MINES = 10       # Number of mines

# Colors for numbers
COLORS = {
    1: "blue",
    2: "green",
    3: "red",
    4: "dark blue",
    5: "brown",
    6: "cyan",
    7: "black",
    8: "grey",
}

# Global variables
board = []         # Matrix with mines and numbers
buttons = []       # Matrix of buttons (the interface)
mines_left = MINES
game_started = False
game_over = False
start_time = 0
timer_id = None

# Create the main window
root = tk.Tk()
root.title("Minesweeper")

# ------------------------ GAME FUNCTIONS ------------------------

def create_board(first_click_row, first_click_col):
    """Creates the board (matrix board) by placing mines and calculating numbers."""
    global board
    board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    mines_placed = 0
    while mines_placed < MINES:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        # Avoid placing a mine on the first clicked cell
        if board[row][col] != "M" and (row != first_click_row or col != first_click_col):
            board[row][col] = "M"
            mines_placed += 1
    # Calculate adjacent numbers
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == "M":
                continue
            count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    rr, cc = r + i, c + j
                    if 0 <= rr < GRID_SIZE and 0 <= cc < GRID_SIZE:
                        if board[rr][cc] == "M":
                            count += 1
            board[r][c] = count

def reveal_adjacent_cells(row, col):
    """Reveals (automatic click) the neighboring cells of a '0' cell."""
    for i in range(-1, 2):
        for j in range(-1, 2):
            r, c = row + i, col + j
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                # Only reveal cells that haven't been revealed and aren't marked
                if not buttons[r][c].revealed and buttons[r][c]["text"] != "!":
                    on_button_click(r, c, is_user_click=False)

def reveal_if_correct_marks(row, col):
    """
    If the revealed cell is a number and has exactly
    the number of "!" markers in its neighbors equal to the number,
    it reveals all adjacent unmarked cells.
    """
    # Only apply this function to numbers (not 0)
    if board[row][col] == 0:
        return

    count_flags = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            r, c = row + i, col + j
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                if buttons[r][c]["text"] == "!":
                    count_flags += 1
    if count_flags == board[row][col]:
        for i in range(-1, 2):
            for j in range(-1, 2):
                r, c = row + i, col + j
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    # Only reveal cells that aren't marked and haven't been revealed yet
                    if not buttons[r][c].revealed and buttons[r][c]["text"] != "!":
                        on_button_click(r, c, is_user_click=False)

def on_button_click(row, col, is_user_click=True):
    """Handles the left click on a cell."""
    global mines_left, game_started, game_over, start_time, timer_id

    if game_over:
        return

    btn = buttons[row][col]

    # If the cell is already revealed, we try to apply the action of revealing neighbors
    if btn.revealed:
        # Only if it's a number (not blank) can the action of revealing neighbors be triggered
        if board[row][col] != 0:
            reveal_if_correct_marks(row, col)
        return

    # If the cell is marked with "!", we do nothing
    if btn["text"] == "!":
        return

    # If it's the first click, we create the board
    if not game_started and is_user_click:
        game_started = True
        create_board(row, col)
        start_time = time.time()
        update_timer()
        reset_button.config(text=":D", font=("Arial", 12, "bold"))

    # If a mine is clicked: YOU LOSE!
    if board[row][col] == "M":
        game_over = True
        # Mark the clicked cell with "X"
        btn.config(text="X", font=("Arial", 12, "bold"), fg="black", bg="red", )
        # Reveal all mines (without changing the appearance of the cells)
        reveal_mines(loss=True)
        reset_button.config(text="D:", font=("Arial", 12, "bold"))
        stop_timer()
    else:
        # Reveal the cell
        if board[row][col] == 0:
            btn.config(text="", bg="lightgray")
        else:
            btn.config(text=str(board[row][col]), font=("Arial", 12, "bold"),
                        bg="lightgray", fg=COLORS.get(board[row][col], "black"))
        btn.revealed = True
        # If it's a "0" cell, we automatically reveal its neighbors
        if board[row][col] == 0:
            reveal_adjacent_cells(row, col)
        check_victory()

def toggle_marker(row, col):
    """Marks or unmarks a cell with '!' (right click)."""
    global mines_left
    btn = buttons[row][col]
    if game_over or btn.revealed:
        return
    if btn["text"] == "!":
        btn.config(text="", font=("Arial", 12, "bold"))
        mines_left += 1
    else:
        if mines_left > 0:
            btn.config(text="!", font=("Arial", 12, "bold"), fg="red")
            mines_left -= 1
    mines_label.config(text=f"Mines: {mines_left}")

def check_victory():
    """Checks if all non-mine cells have been revealed."""
    global game_over
    safe_cells = GRID_SIZE * GRID_SIZE - MINES
    revealed = 0
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if buttons[r][c].revealed and board[r][c] != "M":
                revealed += 1
    if revealed == safe_cells:
        game_over = True
        mark_all_mines()
        reset_button.config(text="8)", font=("Arial", 12, "bold"))
        stop_timer()

def reveal_mines(loss=False):
    """
    Reveals all mines without changing the appearance of the "unpressed" button.
    If loss is True, they are marked with "X". In case of victory, they are marked with "!".
    """
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == "M":
                btn = buttons[r][c]
                # If the user hadn't marked the mine, the corresponding symbol is shown
                if btn["text"] != "!":
                    if loss:
                        btn.config(text="X", font=("Arial", 12, "bold"), fg="black")
                    else:
                        btn.config(text="!", font=("Arial", 12, "bold"), fg="red")
            # If a cell was marked incorrectly (flag on a non-mine cell)
            elif buttons[r][c]["text"] == "!":
                buttons[r][c].config(text="!̶", font=("Arial", 12, "bold"), fg="red")

def mark_all_mines():
    """When winning, marks all mines with '!' without changing their appearance (without pressing)."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == "M":
                buttons[r][c].config(text="!", font=("Arial", 12, "bold"), fg="red")

def update_timer():
    global timer_id
    if game_started and not game_over:
        elapsed = int(time.time() - start_time)
        timer_label.config(text=f"Time: {elapsed}s", font=("Arial", 12, "bold"))
        timer_id = root.after(1000, update_timer)

def stop_timer():
    global timer_id
    if timer_id:
        root.after_cancel(timer_id)
        timer_id = None

def reset_game():
    global mines_left, game_started, game_over, start_time, timer_id
    mines_left = MINES
    game_started = False
    game_over = False
    start_time = 0
    stop_timer()
    timer_label.config(text="Time: 0s", font=("Arial", 12, "bold"))
    reset_button.config(text=":D", font=("Arial", 12, "bold"))
    mines_label.config(text=f"Mines: {MINES}", font=("Arial", 12, "bold"))
    # Reset each button on the board
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            btn = buttons[r][c]
            btn.config(text="", font=("Arial", 12, "bold"), bg="SystemButtonFace", fg="black")
            btn.revealed = False
            # Reset events
            btn.bind("<Button-1>", lambda e, r=r, c=c: on_button_click(r, c))
            btn.bind("<Button-3>", lambda e, r=r, c=c: toggle_marker(r, c))

# ------------------------ GRAPHICAL INTERFACE ------------------------

# Top frame: Mine counter, reset button, and timer
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

mines_label = tk.Label(top_frame, text=f"Mines: {MINES}", font=("Arial", 12, "bold"))
mines_label.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(top_frame, text=":D", font=("Arial", 12, "bold"), command=reset_game)
reset_button.pack(side=tk.LEFT, padx=10)

timer_label = tk.Label(top_frame, text="Time: 0s", font=("Arial", 12, "bold"))
timer_label.pack(side=tk.LEFT, padx=10)

# Board frame
board_frame = tk.Frame(root)
board_frame.pack()

# Create the button matrix
buttons = []
for r in range(GRID_SIZE):
    row_buttons = []
    for c in range(GRID_SIZE):
        btn = tk.Button(board_frame, text="", width=2, height=1, font=("Arial", 12, "bold"))
        btn.grid(row=r, column=c, padx=1, pady=1)
        # Add a custom attribute to know if the cell has been revealed
        btn.revealed = False
        btn.bind("<Button-1>", lambda e, r=r, c=c: on_button_click(r, c))
        btn.bind("<Button-3>", lambda e, r=r, c=c: toggle_marker(r, c))
        row_buttons.append(btn)
    buttons.append(row_buttons)

reset_game()
root.mainloop()