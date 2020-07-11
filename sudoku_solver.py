"""
Sudoku solver with GUI interface
"""

from itertools import chain
from copy import deepcopy
from random import sample
import tkinter as tk
from matplotlib import pyplot as plt


__author__ = "Matthew Woolley"


def sudoku_GUI():
    """
    Displays a GUI to enter the initial sudoku values into, and allows the sudoku program to be activated

    :return: None
    """

    # Define the read_squares event loop function
    def read_squares():
        """
        Reads the entry square values, checks they are valid and executes the sudoku solver

        Called when the 'Solve' button is clicked
        :return: None
        """

        # Get the value of all the entry squares
        squares = [square_entry.get() for square_entry in square_entries]
        # Check all of the square values are valid
        if all([is_valid_square_input(square) for square in squares]) is False:
            lbl_error.config(text="One or more inputs is incorrect\nAll inputs must be integers >= 1 and <= 9\nPlease try again", font="Calibri 15", bg="red", fg="black")
        else:
            # Convert the square values to a starting grid
            squares_numeric = [int(square) if square != "" else 0 for square in squares]
            starting_grid = [squares_numeric[9 * i:9 * i + 9] for i in range(9)]
            # Check that the starting grid does not contain any duplicates
            if is_valid_starting_grid(starting_grid):
                lbl_error.config(text="Successful input", font="Calibri 15", bg="green", fg="white")
                sudoku_solver(starting_grid)
            else:
                lbl_error.config(text="One or more inputs is incorrect\nThere can be no repeats in rows, columns or boxes\nPlease try again", font="Calibri 15", bg="red", fg="black")

    root = tk.Tk()

    lbl_title = tk.Label(text="Sudoku Solver", font="Calibri 30")
    lbl_title.pack()

    # Create the squares of the sudoku
    square_entries = []
    for row in range(9):
        # Create a frame for each row
        frm_row = tk.Frame()
        frm_row.pack()
        for col in range(9):
            # Alterate boxes white and grey
            if row_col2box(row, col) % 2 == 0:
                square_col = "white"
            else:
                square_col = "grey"
            ent_square = tk.Entry(master=frm_row, justify="center", width=3, font="Calibri 30", bg=square_col)
            ent_square.pack(side=tk.LEFT)
            square_entries.append(ent_square)


    # All some padding between the sudoku and the solve button
    frm_blank = tk.Frame(height=20)
    frm_blank.pack()

    # Create solve button and tie it to the read_squares function
    btn_solve = tk.Button(text="Solve", relief=tk.RAISED, font="Calibri 20", bg="white", command=read_squares)
    btn_solve.pack(side=tk.RIGHT)

    # Create the errors label
    lbl_error = tk.Label(text="", bg=None)
    lbl_error.pack()

    root.mainloop()


def is_valid_starting_grid(starting_grid):
    """
    Checks if a starting grid contains duplicates in any rows, columns or boxes

    :param starting_grid: Starting grid of the sudoku, len(9) list of len(9) lists of ints
    :return: True if no repeats, False if repeats present
    """

    # Each row has no duplicates
    for row in starting_grid:
        if len(set(row) - {0}) != 9 - row.count(0):
            return False

    # Each column has no duplicates
    for col_num in range(9):
        col = [starting_grid[i][col_num] for i in range(9)]
        if len(set(col) - {0}) != 9 - col.count(0):
            return False

    # Each box has no duplicates
    for box_num in range(9):
        box_start_row_num, box_start_col_num = box2start_row_col(box_num)
        box = [starting_grid[box_start_row_num + delta // 3][box_start_col_num + delta % 3] for delta in range(9)]
        if len(set(box) - {0}) != 9 - box.count(0):
            return False

    return True


def is_valid_square_input(text):
    """
    Checks if an entry square value is a valid input to the sudoku

    :param text: Str
    :return: True if valid, False if not
    """

    if text == "" or (text.isdigit() and 1 <= int(text) <= 9):
        return True
    else:
        return False


def sudoku_display(output_grid):
    """
    Display the solved sudoku as a figure

    :param output_grid: The solved sudoku, len(9) list of len(9) lists of ints
    :return: None
    """

    # Generate colour array, alternating boxes white and grey
    colour_grid = [['white' if row_col2box(row, col) % 2 == 0 else 'grey' for col in range(9)] for row in range(9)]

    # Print the solved sudoku
    sudoku_table = plt.table(cellText=output_grid, cellColours=colour_grid, loc="upper center", cellLoc="center")
    sudoku_table.scale(2/3, 2)
    plt.title("Solved Sudoku")
    plt.axis("off")
    plt.show()


def sudoku_solver(starting_grid):
    """
    Solves the sudoku (if possible)

    :param starting_grid: Representation of the given squares, len(9) list of len(9) lists of ints
    :return: None
    """

    # Create a copy of the starting grid so as not to modify the original
    # Not important for GUI use, but modifying the original may cause problems in backend testing
    output_grid = deepcopy(starting_grid)
    # Create lists of the squares with only one option and a grid of all the squares' options
    single_option_squares, options_grid = initialise_grid(starting_grid)
    # Use first_time to access the while loops in sudoku_solver_sub_func if no squares
    # with a single option have been found
    first_time = True

    output_grid = sudoku_solver_sub_func(options_grid, output_grid, single_option_squares, first_time)

    # If the sudoku could be solved, display
    if output_grid is not False:
        sudoku_display(output_grid)
    else:
        plt.title("Unable to solve sudoku")
        plt.show()


def sudoku_solver_sub_func(options_grid, output_grid, single_option_squares, first_time):
    """
    Recursive component of sudoku_solver

    :param options_grid: Grid of the options for each square, len(9) list of len(9) lists of sets of ints
    :param output_grid: Grid of the found squares, len(9) list of len(9) lists of ints
    :param single_option_squares: Set of the squares with a single option that have not yet been processed,
        set of len(2) tuples of ints
    :param first_time: Use first_time to access the while loops in sudoku_solver_sub_func if no squares
        with a single option have been found
    :return output grid: EITHER len(9) list of len(9) lists of ints, OR False
    """

    # Stay in the loop as long as there are more single-option squares to be processed (or first time)
    while len(single_option_squares) > 0 or first_time is True:
        if first_time is True:
            first_time = False

        # Process single-option squares until no more remain
        if single_number_elimination(options_grid, output_grid, single_option_squares) is False:
            return False

        # Check if the sudoku is complete
        if is_sudoku_complete(output_grid):
            return output_grid

        # Utilise the scanning technique to find more single-option squares
        grid_scanning(options_grid, single_option_squares)

    # If no more single-option squares can be found, create new branches from the square with the fewest options
    # Find least-options square
    min_options_row, min_options_col = minimum_options_square(options_grid)
    # Iterate over the options
    for option in options_grid[min_options_row][min_options_col]:
        # Create copies of all objects to avoid overwriting between branches
        options_grid2 = deepcopy(options_grid)
        output_grid2 = deepcopy(output_grid)
        single_option_squares2 = deepcopy(single_option_squares)
        # Set the least-options square equal to one option and add to single-options squares set
        options_grid2[min_options_row][min_options_col] = {option}
        single_option_squares2.add((min_options_row, min_options_col))
        # Call recursively
        output_grid3 = sudoku_solver_sub_func(options_grid2, output_grid2, single_option_squares2, first_time)
        # If the sudoku became unsolvable, try the next option
        if output_grid3 is False:
            continue
        # Return the successful solution
        else:
            return output_grid3

    # If no option produces a solvable sudoku, then there was an undetected issue with the starting grid
    # Return False to indicate sudoku is unsolvable
    return False


def minimum_options_square(options_grid):

    min_num_options = float('inf')
    for row in range(9):
        for col in range(9):
            if 1 < len(options_grid[row][col]) < min_num_options:
                min_num_options = len(options_grid[row][col])
                min_options_row = row
                min_options_col = col

    return min_options_row, min_options_col


def is_sudoku_complete(output_grid):

    if any([any([square == 0 for square in row]) for row in output_grid]):
        return False
    else:
        return True

def single_number_elimination(options_grid, output_grid, single_option_squares):

    while len(single_option_squares) > 0:
        row, col = single_option_squares.pop()
        [output_grid[row][col]] = options_grid[row][col]

        # Row
        for col2 in range(9):
            if col != col2:
                options_grid[row][col2] -= options_grid[row][col]
                if len(options_grid[row][col2]) == 0:
                    return False
                elif len(options_grid[row][col2]) == 1 and output_grid[row][col2] == 0:
                    single_option_squares.add((row, col2))

        # Column
        for row2 in range(9):
            if row != row2:
                options_grid[row2][col] -= options_grid[row][col]
                if len(options_grid[row2][col]) == 0:
                    return False
                elif len(options_grid[row2][col]) == 1 and output_grid[row2][col] == 0:
                    single_option_squares.add((row2, col))


        # Box
        box = row_col2box(row, col)
        box_start_row = 3 * (box // 3)
        box_start_col = 3 * (box % 3)
        for delta in range(9):
            row_delta = delta // 3
            col_delta = delta % 3
            row2 = box_start_row + row_delta
            col2 = box_start_col + col_delta
            if row != row2 or col != col2:
                options_grid[row2][col2] -= options_grid[row][col]
                if len(options_grid[row2][col2]) == 0:
                    return False
                elif len(options_grid[row2][col2]) == 1 and output_grid[row2][col2] == 0:
                    single_option_squares.add((row2, col2))


    return


def grid_scanning(options_grid, single_option_squares):

    # Rows
    for row in sample(range(9), 9):
        for col in sample(range(9), 9):
            if len(options_grid[row][col]) > 1:
                options = options_grid[row][col].copy()
                for col2 in range(9):
                    if col != col2:
                        options -= options_grid[row][col2]
                        if len(options) == 0:
                            break
                else:
                    if len(options) == 1:
                        single_option_squares.add((row, col))
                        options_grid[row][col] = options
                        return True

    # Columns
    for col in sample(range(9), 9):
        for row in sample(range(9), 9):
            if len(options_grid[row][col]) > 1:
                options = options_grid[row][col].copy()
                for row2 in range(9):
                    if row != row2:
                        options -= options_grid[row2][col]
                        if len(options) == 0:
                            break
                else:
                    if len(options) == 1:
                        single_option_squares.add((row, col))
                        options_grid[row][col] = options
                        return True

    # Boxes
    for box in sample(range(9), 9):
        box_start_row = 3 * (box // 3)
        box_start_col = 3 * (box % 3)
        for row_delta in sample(range(3), 3):
            row = box_start_row + row_delta
            for col_delta in sample(range(3), 3):
                col = box_start_col + col_delta
                if len(options_grid[row][col]) > 1:
                    options = options_grid[row][col].copy()
                    for i in range(9):
                        row2 = box_start_row + i // 3
                        col2 = box_start_col + i % 3
                        if row != row2 or col != col2:
                            options -= options_grid[row2][col2]
                            if len(options) == 0:
                                break
                    else:
                        if len(options) == 1:
                            single_option_squares.add((row, col))
                            options_grid[row][col] = options

    return


def initialise_grid(starting_grid):

    single_option_squares = set()

    row_options = []
    for row in starting_grid:
        set1 = set(range(1, 10))
        set2 = set(row)
        row_options.append(set1 - set2)

    column_options = []
    for col_num in range(9):
        set1 = set(range(1, 10))
        set2 = set([starting_grid[row_num][col_num] for row_num in range(9)])
        column_options.append(set1 - set2)

    box_options = []
    for i in range(3):
        for j in range(3):
            x = [[starting_grid[3 * i + m][3 * j + n] for m in range(3)] for n in range(3)]
            set1 = set(range(1, 10))
            set2 = set(chain.from_iterable(x))
            box_options.append(set1 - set2)

    options_grid = []
    for row in range(9):
        options_row = []
        for col in range(9):
            if starting_grid[row][col] != 0:
                options_row.append({starting_grid[row][col]})
            else:
                options = row_options[row] & column_options[col] & box_options[row_col2box(row, col)]
                options_row.append(options)
                if len(options) == 1:
                    single_option_squares.add((row, col))
        options_grid.append(options_row)

    return single_option_squares, options_grid


def row_col2box(row_num, col_num):
    """
    Converts the row and column number into the corresponding box number

    :param row_num: Int
    :param col_num: Int
    :return box_num: Int
    """

    row_group_num = row_num // 3
    col_group_num = col_num // 3
    box_num = 3 * row_group_num + col_group_num

    return box_num


def box2start_row_col(box_num):
    """
    Converts the box number to the corresponding row and column number of the square in the upper left corner of the box

    :param box_num: Int
    :return: len(2) tuple
        [1] start_row_num: Int
        [2] start_col_num: Int
    """

    start_row_num = 3 * (box_num // 3)
    start_col_num = 3 * (box_num % 3)

    return start_row_num, start_col_num


starting_arrangement_easy = [
                    [0, 0, 0, 0, 0, 0, 9, 2, 6],
                    [2, 6, 0, 9, 1, 0, 5, 0, 0],
                    [0, 5, 4, 0, 3, 0, 0, 0, 0],
                    [6, 0, 0, 8, 0, 5, 0, 9, 7],
                    [8, 0, 0, 0, 0, 0, 0, 0, 1],
                    [5, 4, 0, 1, 0, 9, 0, 0, 2],
                    [0, 0, 0, 0, 2, 0, 1, 6, 0],
                    [0, 0, 2, 0, 9, 6, 0, 3, 5],
                    [3, 8, 6, 0, 0, 0, 0, 0, 0]
                    ]


starting_arrangement_medium = [
                    [0, 0, 6, 0, 0, 0, 0, 0, 0],
                    [2, 0, 0, 5, 0, 7, 3, 0, 0],
                    [0, 0, 3, 6, 0, 0, 0, 8, 4],
                    [0, 4, 0, 7, 5, 2, 0, 3, 0],
                    [8, 0, 7, 0, 0, 0, 4, 0, 0],
                    [0, 0, 0, 0, 0, 9, 0, 0, 0],
                    [9, 6, 2, 0, 0, 0, 0, 0, 5],
                    [1, 0, 0, 0, 2, 4, 0, 6, 3],
                    [0, 7, 0, 0, 0, 0, 0, 2, 0]
                    ]

starting_arrangement_hard = [
                    [4, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 9, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 7, 8, 5],
                    [0, 0, 7, 0, 4, 8, 0, 5, 0],
                    [0, 0, 1, 3, 0, 0, 0, 0, 0],
                    [0, 0, 6, 0, 7, 0, 0, 0, 0],
                    [8, 6, 0, 0, 0, 0, 9, 0, 3],
                    [7, 0, 0, 0, 0, 5, 0, 6, 2],
                    [0, 0, 3, 7, 0, 0, 0, 0, 0]
                    ]

starting_arrangement_expert = [
                    [3, 0, 0, 0, 0, 0, 7, 8, 0],
                    [0, 6, 0, 4, 0, 0, 3, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 5, 0],
                    [9, 0, 0, 8, 1, 0, 0, 0, 0],
                    [8, 0, 0, 3, 0, 0, 0, 2, 0],
                    [0, 7, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 3, 9, 0, 4],
                    [7, 0, 0, 5, 8, 0, 0, 0, 0],
                    [0, 0, 9, 0, 0, 6, 0, 0, 5]
                    ]

sudoku_GUI()