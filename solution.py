
# === Sudoku board confing ===

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s + t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

#Additional units used for Diagonal Sudoku
diagonal1 = [[rows[a] + cols[a] for a in range(0, 9)]]
diagonal2 = [[rows[8 - a] + cols[a] for a in range(0, 9)]]
diagonals = diagonal1 + diagonal2

unitlist = row_units + column_units + square_units + diagonals
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

# ===END OF Sudoku board confing ===

def count_unsolved(values):
    """
    Count of unsolved boxes in Sudoku
    Input: The sudoku in dictionary form
    Output: Number of unsolved boxes in Sudoku (should be 0 when Sudoku is Solved)
    """
    return len([box for box in values.keys() if len(values[box]) == 1])


def count_values_chars(values):
    """
    Count overall number of characters in Sudoku. Value for solved 9x9 Sudoku should be 81.
    Input: The sudoku in dictionary form
    Output: The number of all characters in Sudoku (81 for Solved sudoku, more than 81 if there are still any
     boxes with multiple digits.
    """
    count = 0
    for box in boxes:
        count += len(values[box])

    return count


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """
    Find naked twins in unit and eliminate each twin digit from any other box in this unit. Do in loop until there
    are no more changes in Sudoku values.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary after eliminating values.
    """
    while True:
        solved_values_before = count_values_chars(values)

        for unit in (row_units + column_units):
            two_digits_boxes = [(box, values[box]) for box in unit if len(values[box]) == 2]
            if len(two_digits_boxes) >= 2:
                seen_values = set()
                twin_values = []
                for box, value in two_digits_boxes:
                    if value in seen_values:
                        twin_values.append(value)
                    else:
                        seen_values.add(value)

                for twin_value in twin_values:
                    for box_in_unit in unit:
                        #skip twins
                        if values[box_in_unit] == twin_value:
                            continue

                        for digit in twin_value:
                            assign_value(values, box_in_unit, values[box_in_unit].replace(digit, ''))
                            # values[box_in_unit] = values[box_in_unit].replace(digit, '')

        solved_values_after = count_values_chars(values)

        # If no more changes in values, stop the loop.
        if solved_values_before == solved_values_after:
            break

    return values


def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '.' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '.' if it is empty.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"

    box_values = []
    for char in grid:
        box_values.append('123456789' if char == '.' else char)

    return dict(zip(boxes, box_values))


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_boxes = []
    for box in values.keys():
        if len(values[box]) == 1:
            solved_boxes.append(box)

    for solved_box in solved_boxes:
        solved_digit = values[solved_box]
        for peer in peers[solved_box]:
            assign_value(values, peer, values[peer].replace(solved_digit, ''))
            # values[peer] = values[peer].replace(solved_digit, '')

    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            digit_places = [box for box in unit if digit in values[box]]
            if (len(digit_places)) == 1:
                values[digit_places[0]] = digit

    return values


def reduce_puzzle(values):
    """
    Iterate eliminate(), naked_twins() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    while True:
        solved_values_before = count_unsolved(values)

        values = eliminate(values)
        values = naked_twins(values)
        values = only_choice(values)

        solved_values_after = count_unsolved(values)
        if solved_values_before == solved_values_after:
            break

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """
    "Using depth-first search and propagation, create a search tree and solve the Sudoku."
    """
    values = reduce_puzzle(values)
    if values == False:
        return False

    if all(len(values[s]) == 1 for s in boxes):
        return values

    box_len, min_box = min((len(values[min_box]), min_box) for min_box in boxes if len(values[min_box]) > 1)

    for possible_val in values[min_box]:
        temp_values = values.copy()
        temp_values[min_box] = possible_val
        solved = search(temp_values)
        if solved:
            return solved


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
