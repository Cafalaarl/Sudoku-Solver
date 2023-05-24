# Sudoku solver using backtracking

def print_grid(grid):
    # prints the provided sudoku grid
    for i in range(9):
        for j in range(9):
            print(grid[i][j], end=' ')
        print()


def find_empty(grid, empty):
    # scans grid for and empty(0) spot
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                empty[0] = i
                empty[1] = j
                return True
    return False


def in_row(grid, row, num):
    # checks if number is in provided row
    for i in grid[row]:
        if i == num:
            return True
    return False


def in_col(grid, col, num):
    # checks if number is in provided column
    for i in grid:
        if i[col] == num:
            return True
    return False


def in_box(grid, row, col, num):
    # checks if number in 3x3 box
    for i in range(3):
        for j in range(3):
            if grid[i + row][j + col] == num:
                return True
    return False


def check_if_safe(grid, row, col, num):
    # checks if spot is safe for number
    # according to sudoku rules
    return (not in_row(grid, row, num)) and (not in_col(grid, col, num)) and\
           (not in_box(grid, row - row % 3, col - col % 3, num))


def solve_sudoku(grid):
    # solves a partially filled sudoku

    # list to keep track of position of empty spot
    empty = [0, 0]

    if not find_empty(grid, empty):
        return True

    # assigns location of found empty spot
    row = empty[0]
    col = empty[1]

    for num in range(1, 10):

        # checks if number can be put in position according to sudoku rules
        if check_if_safe(grid, row, col, num):

            grid[row][col] = num

            # return if sudoku is solved with this addition
            if solve_sudoku(grid):
                return True

            # resets position if sudoku was unsolved
            grid[row][col] = 0

    # backtracking if sudoku unsolved
    return False


if __name__ == "__main__":

    grid = [[0 for x in range(9)] for y in range(9)]

    grid = [[3, 0, 6, 5, 0, 8, 4, 0, 0],
            [5, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 8, 7, 0, 0, 0, 0, 3, 1],
            [0, 0, 3, 0, 1, 0, 0, 8, 0],
            [9, 0, 0, 8, 6, 3, 0, 0, 5],
            [0, 5, 0, 0, 9, 0, 6, 0, 0],
            [1, 3, 0, 0, 0, 0, 2, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 7, 4],
            [0, 0, 5, 2, 0, 6, 3, 0, 0]]

    if solve_sudoku(grid):
        print_grid(grid)
    else:
        print("unsolvable")
