import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import random




def validate_input(text):
    return (text.isdigit() and 1 <= int(text) <= 9) or text == ""

#генерация доски
def generate_full_board():
    board = [[0]*9 for _ in range(9)]


    def is_valid(brd, rows, colums, val):
        if any(brd[rows][j] == val for j in range(9)): return False
        if any(brd[i][colums] == val for i in range(9)): return False
        br, bc = (rows//3)*3, (colums//3)*3
        for i in range(br, br+3):
            for j in range(bc, bc+3):
                if brd[i][j] == val: return False
        return True


    def fill(brd):
        for i in range(9):
            for j in range(9):
                if brd[i][j] == 0:
                    digits = list(range(1,10))
                    random.shuffle(digits)
                    for n in digits:
                        if is_valid(brd, i, j, n):
                            brd[i][j] = n
                            if fill(brd):
                                return True
                            brd[i][j] = 0
                    return False
        return True

    fill(board)
    return board


def remove_cells(board, difficulty):

    if difficulty == "easy":
        remove_count = 36
    elif difficulty == "medium":
        remove_count = 46
    else:
        remove_count = 54

    puzzle = [row[:] for row in board]
    
    cells = [(r,c) for r in range(9) for c in range(9)]

    random.shuffle(cells)
    removed = 0
    for rows,colums in cells:
        if removed >= remove_count:
            break
        puzzle[rows][colums] = 0
        removed += 1
    return puzzle

# заполнить клетки и отключить их
def fill_puzzle(puzzle, solution):
    for rows in range(9):
        for colums in range(9):
            e = entries[rows][colums]
            e.config(state="normal", bg=cell_bg)
            e.delete(0, tk.END)
            if puzzle[rows][colums] != 0:
                e.insert(0, str(puzzle[rows][colums]))
                e.config(state="disabled", disabledforeground="black", disabledbackground=disabled_bg)
    global current_solution, initial_puzzle
    current_solution = solution
    initial_puzzle = [row[:] for row in puzzle]

# показать решение

def show_solution():
    if current_solution is None:
        messagebox.showinfo("Решение", "Сначала сгенерируйте пазл.")
        return
    for rows in range(9):
        for colums in range(9):
            e = entries[rows][colums]
            e.config(state="normal")
            e.delete(0, tk.END)
            e.insert(0, str(current_solution[rows][colums]))
            e.config(state="disabled", disabledforeground="blue", disabledbackground=solution_bg)

# сделать матрицу

def read_board_from_entries():
    board = [[0]*9 for _ in range(9)]
    for rows in range(9):
        for colums in range(9):
            val = entries[rows][colums].get()
            board[rows][colums] = int(val) if val.isdigit() else 0
    return board

# проверка заполнения
def find_conflicts(board):
    conflicts = set()
    # строки
    for rows in range(9):
        seen = {}
        for colums in range(9):
            digit = board[rows][colums]
            if digit == 0: continue
            if digit in seen:
                conflicts.add((rows,colums))
                conflicts.add((rows,seen[digit]))
            else:
                seen[digit] = colums
    # столбцы
    for colums in range(9):
        seen = {}
        for rows in range(9):
            digit = board[rows][colums]
            if digit == 0: continue
            if digit in seen:
                conflicts.add((rows,colums))
                conflicts.add((seen[digit],colums))
            else:
                seen[digit] = rows
    # блоки 3x3
    for blockRows in range(3):
        for blockColums in range(3):
            seen = {}
            for i in range(3):
                for j in range(3):
                    rows = blockRows*3 + i
                    colums = blockColums*3 + j
                    digit = board[rows][colums]
                    if digit == 0: continue
                    if digit in seen:
                        conflicts.add((rows,colums))
                        conflicts.add(seen[digit])
                    else:
                        seen[digit] = (rows,colums)
    return conflicts

# проверка решения
def check_solution():
    if current_solution is None:
        messagebox.showinfo("Проверка", "Сначала сгенерируйте пазл.")
        return

    board = read_board_from_entries()

    # сброс подсветки
    for rows in range(9):
        for colums in range(9):
            e = entries[rows][colums]
            if initial_puzzle[rows][colums] != 0:
                e.config(bg=disabled_bg)
            else:
                e.config(bg=cell_bg)

    # проверка на незаполненные клетки
    if any(board[rows][colums] == 0 for rows in range(9) for colums in range(9)):
        messagebox.showwarning("Проверка", "Пазл не заполнен полностью.")
        return

    # сравнение с ориг. пешением
    if board == current_solution:
        messagebox.showinfo("Проверка", "Отлично! Решение верное и совпадает с оригиналом.")
        for rows in range(9):
            for colums in range(9):
                entries[rows][colums].config(bg=success_bg)
        return

    # при несовпадении ищем ошибки
    conflicts = find_conflicts(board)
    if conflicts:
        for (rows,colums) in conflicts:
            entries[rows][colums].config(bg=conflict_bg)
        messagebox.showerror("Проверка", "Найдены конфликты в решении. Красные клетки — проблемные.")
        return

    messagebox.showinfo("Проверка", "Поле корректно по правилам, но отличается от оригинального решения.")

# генератор пазла
def generate_puzzle():
    diff = difficulty_var.get()
    full = generate_full_board()
    puzzle = remove_cells(full, diff)
    fill_puzzle(puzzle, full)

# gui
root = tk.Tk()
root.title("Судоку")

# окно
WINDOW_W, WINDOW_H = 600, 760
root.geometry(f"{WINDOW_W}x{WINDOW_H}")
root.resizable(False, False)
root.minsize(WINDOW_W, WINDOW_H)
root.maxsize(WINDOW_W, WINDOW_H)

# бэкграунд
app_bg = "#b3b1b1"        # общий фон окна
grid_gap_bg = "#888888"   # фон между клетками
disabled_bg = "#afafaf"   # фон заполненых кодом клеток
cell_bg = "#f0f0f0"         # фон незаполненных клеток
solution_bg = "#dfefff"     # фон при показе решения
success_bg = "#e6ffe6"      # фон правильных клеток
conflict_bg = "#ffd6d6"     # фон ошибок

root.configure(bg=app_bg)

vcmd = (root.register(validate_input), "%P")

# верзняя панель
top_frame = tk.Frame(root, bg=app_bg)
top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)
top_frame.grid_columnconfigure(2, weight=1)

difficulty_var = tk.StringVar(value="easy")
rb_easy = tk.Radiobutton(top_frame, text="Легко", variable=difficulty_var, value="easy", bg=app_bg)
rb_medium = tk.Radiobutton(top_frame, text="Средне", variable=difficulty_var, value="medium", bg=app_bg)
rb_hard = tk.Radiobutton(top_frame, text="Сложно", variable=difficulty_var, value="hard", bg=app_bg)
rb_easy.grid(row=0, column=0, sticky="w")
rb_medium.grid(row=0, column=1)
rb_hard.grid(row=0, column=2, sticky="e")

btn_frame = tk.Frame(root, bg=app_bg)
btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))
btn_frame.grid_columnconfigure(0, weight=1)
btn_frame.grid_columnconfigure(1, weight=1)
btn_generate = tk.Button(btn_frame, text="Сгенерировать пазл", command=generate_puzzle, font=("Arial", 12))
btn_solution = tk.Button(btn_frame, text="Показать решение", command=show_solution, font=("Arial", 12))
btn_generate.grid(row=0, column=0, sticky="ew", padx=(0,6))
btn_solution.grid(row=0, column=1, sticky="ew", padx=(6,0))




# Настройка сетки внутри фрейма
for i in range(9):
    grid_frame.grid_rowconfigure(i, weight=1)
    grid_frame.grid_columnconfigure(i, weight=1)



shared_font = tkfont.Font(family="Arial", size=20)
entries = [[None for _ in range(9)] for _ in range(9)]

for rows in range(9):
    for colums in range(9):
        e = tk.Entry(grid_frame, font=shared_font, justify="center",
                     validate="key", validatecommand=vcmd, bd=1, relief="solid",
                     disabledbackground=disabled_bg)
        left = 4 if colums % 3 == 0 else 2
        right = 4 if colums % 3 == 2 else 2
        top = 4 if rows % 3 == 0 else 2
        bottom = 4 if rows % 3 == 2 else 2
        e.grid(row=rows, column=colums, sticky="nsew", padx=(left, right), pady=(top, bottom))
        entries[rows][colums] = e

# Кнопка проверки решения
btn_check = tk.Button(root, text="Проверить решение", command=check_solution, font=("Arial", 12))
btn_check.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,10))

# Квадратные клетки: при старте подстраиваем minsize и шрифт,
# но шрифт не станет меньше базового 20 пикселей
def on_start_resize():
    width = grid_frame.winfo_width()
    height = grid_frame.winfo_height()
    if width <= 0 or height <= 0:
        return
    cell_size = int(min(width / 9, height / 9))
    for i in range(9):
        grid_frame.grid_rowconfigure(i, minsize=cell_size)
        grid_frame.grid_columnconfigure(i, minsize=cell_size)
    # шрифт не опустится ниже 20
    new_font_size = max(20, int(cell_size * 0.55))
    shared_font.configure(size=new_font_size)

root.update_idletasks()
on_start_resize()

# Глобальные переменные
current_solution = None
initial_puzzle = [[0]*9 for _ in range(9)]

root.mainloop()
