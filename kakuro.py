import time
from PIL import Image, ImageDraw, ImageFont

class KakuroPuzzle:
    def __init__(self, row_clues, col_clues, case):
        self.count = 0
        self.case = case
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.rows = max(row[0] for row in row_clues) + 1
        self.cols = max(col[0] for col in col_clues) + 1
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.clue_grids = []
        self.empty_grids = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        for row in row_clues:
            self.board[row[0]][row[1]-1] = row[3]
            self.clue_grids.append((row[0],row[1]-1))
            for j in range(row[1]-1,row[2]+1):
                if self.empty_grids.count((row[0],j)) > 0:
                    self.empty_grids.remove((row[0],j))
        for col in col_clues:
            self.board[col[1]-1][col[0]] = col[3]
            self.clue_grids.append((col[1]-1,col[0]))
            for i in range(col[1]-1,col[2]+1):
                if self.empty_grids.count((i,col[0])) > 0:
                    self.empty_grids.remove((i,col[0]))
        self.question = [[self.board[i][j] for j in range(self.cols)] for i in range(self.rows)]

    def is_solution(self):
        for row in self.row_clues:
            if sum(self.board[row[0]][i] for i in range(row[1], row[2] + 1)) != row[3]:
                return False

        for col in self.col_clues:
            if sum(self.board[i][col[0]] for i in range(col[1], col[2] + 1)) != col[3]:
                return False

        return True

    def solve_backtrack(self):
        self.count = 0
        return self._solve_bactrack_helper(0, 0)

    def _solve_bactrack_helper(self, row, col):
        self.count += 1
        # self.draw_solution("./case"+str(self.case)+"/backtrack/"+str(self.count))
        if row > self.rows - 1:
            return self.is_solution()

        next_row = row + 1 if col == self.cols - 1 else row
        next_col = 1 if col == self.cols - 1 else col + 1

        if self.board[row][col] != 0:
            return self._solve_bactrack_helper(next_row, next_col)

        if (row,col) not in self.empty_grids:
            for num in range(9,0,-1):
                if self.is_valid(row, col, num):
                    self.board[row][col] = num

                    if self._solve_bactrack_helper(next_row, next_col):
                        return True

                    self.board[row][col] = 0
        
        if (row,col) in self.empty_grids and self._solve_bactrack_helper(next_row, next_col):
            return True

        return False
    
    def solve_brute_force(self):
        self.count = 0
        return self._solve_brute_force_helper(0, 0)

    def _solve_brute_force_helper(self, row, col):
        self.count += 1
        # self.draw_solution("./case"+str(self.case)+"/brute force/"+str(self.count))
        if row > self.rows - 1:
            if self.is_solution() and self.is_unique():
                return True
            return False

        next_row = row + 1 if col == self.cols - 1 else row
        next_col = 1 if col == self.cols - 1 else col + 1

        if (row,col) not in self.empty_grids:
            if self.board[row][col] != 0:
                return self._solve_brute_force_helper(next_row, next_col)

            for num in range(9,0,-1):
                self.board[row][col] = num

                if self._solve_brute_force_helper(next_row, next_col):
                    return True

            self.board[row][col] = 0

        if (row,col) in self.empty_grids and self._solve_brute_force_helper(next_row, next_col):
            return True

        return False

    def is_unique(self):   
        solution = [[self.board[i][j] - self.question[i][j] for j in range(self.cols)] for i in range(self.rows)]
        # Check rows
        for row in solution:
            row_values = []
            for j in range(self.cols):
                if row[j] != 0:
                    row_values.append(row[j])
            if len(row_values) != len(set(row_values)):
                return False

        # Check columns
        for col in range(self.cols):
            column_values = []
            for i in range(self.rows):
                if solution[i][col] != 0:
                    column_values.append(solution[i][col])
            if len(column_values) != len(set(column_values)):
                return False

        return True

    def is_valid(self, row, col, num):
        # Check if the number is already present in the row
        i = 0
        while self.row_clues[i][0] != row:
            i += 1
        if num in self.board[row][self.row_clues[i][1]:self.row_clues[i][2]+1]:
            return False
        if num > self.row_clues[i][3]:
            return False

        # Check if the number is already present in the column
        j = 0
        while self.col_clues[j][0] != col:
            j += 1
        for i in range(self.col_clues[j][1], self.col_clues[j][2]+1):
            if num == self.board[i][col]:
                return False
        if num > self.col_clues[j][3]:
            return False
            

        # Check the row clues
        for clue in self.row_clues:
            if row == clue[0] and col >= clue[1] and col <= clue[2]:
                total = sum(self.board[row][clue[1] : clue[2] + 1])
                if total > clue[3]:
                    return False
                if total == clue[3] and self.board[row][col] != 0:
                    return False

        # Check the column clues
        for clue in self.col_clues:
            if col == clue[0] and row >= clue[1] and row <= clue[2]:
                total = sum(self.board[i][col] for i in range(clue[1], clue[2] + 1))
                if total > clue[3]:
                    return False
                if total == clue[3] and self.board[row][col] != 0:
                    return False

        return True

    def print_solution(self):
        for row in self.board:
            print(row)

    def draw_solution(self,title):
        cell_size = 30
        border_size = 2

        image_width = self.cols * cell_size + (self.cols + 1) * border_size
        image_height = self.rows * cell_size + (self.rows + 1) * border_size

        image = Image.new("RGB", (image_width, image_height), "black")
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype("arial.ttf", cell_size//2)
        clue_font = ImageFont.truetype("arial.ttf", cell_size//3)

        for i in range(self.rows):
            for j in range(self.cols):
                if (i,j) not in self.empty_grids and (i,j) not in self.clue_grids:
                    color = "white"
                    x1 = j * cell_size + (j + 1) * border_size
                    y1 = i * cell_size + (i + 1) * border_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    draw.rectangle([x1, y1, x2, y2], fill=color)
                    if self.board[i][j] != 0:
                        draw.text((x1+cell_size//3,y1+cell_size//3), str(self.board[i][j]), fill="black", font=font)

        # Draw the vertical grid lines
        for i in range(self.cols + 1):
            x = i * (cell_size + border_size)
            y1 = 0
            y2 = image_height
            draw.line([(x, y1), (x, y2)], fill="black", width=border_size)

        for row in self.row_clues:
            x1 = (row[1] - 1) * cell_size + row[1] * border_size
            y1 = row[0] * cell_size + (row[0] + 1) * border_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            draw.polygon([(x1, y1), (x2, y2), (x2,y1)], fill="gray")
            draw.line([(x1, y1), (x2, y2)], fill="black", width=2)
            draw.text((x1+2*cell_size//3,y1+cell_size//7), str(row[3]), fill="black", font=clue_font)

        for col in self.col_clues:
            x1 = col[0] * cell_size + (col[0] + 1) * border_size
            y1 = (col[1] - 1) * cell_size + col[1] * border_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            draw.polygon([(x1, y1), (x2, y2), (x1,y2)], fill="gray")
            draw.line([(x1, y1), (x2, y2)], fill="black", width=2)
            draw.text((x1+cell_size//4,y1+cell_size//2), str(col[3]), fill="black", font=clue_font)
        
        # Draw the horizontal grid lines
        for i in range(self.rows + 1):
            y = i * (cell_size + border_size)
            x1 = 0
            x2 = image_width
            draw.line([(x1, y), (x2, y)], fill="black", width=border_size)

        image.save(title + ".png")


# Example usage
r_clues = []
c_clues = []

r_clues.append([
    [1, 1, 2, 9],
    [2, 1, 2, 6],
])

c_clues.append([
    [1, 1, 2, 12],
    [2, 1, 2, 3],
])

r_clues.append([
    [1, 2, 3, 4],
    [2, 1, 3, 7],
    [3, 1, 3, 6],
])

c_clues.append([
    [1, 2, 3, 4],
    [2, 1, 3, 7],
    [3, 1, 3, 6],
])

r_clues.append([
    [1,1,2,13],
    [2,1,3,12],
    [3,2,3,3]
])

c_clues.append([
    [1,1,2,5],
    [2,1,3,19],
    [3,2,3,4]
])

r_clues.append([
    [1, 1, 3, 18],
    [2, 1, 3, 11],
    [3, 1, 3, 18]
])

c_clues.append([
    [1, 1, 3, 11],
    [2, 1, 3, 22],
    [3, 1, 3, 14]
])

for i in range(len(r_clues)):
    row_clues = r_clues[i]
    col_clues = c_clues[i]
    print("case", i+1)
    print("Backtrack")
    puzzle = KakuroPuzzle(row_clues, col_clues, i+1)
    puzzle.draw_solution("question " + str(i+1))
    start = time.perf_counter()
    if puzzle.solve_backtrack():
        print("Solution found:")
        puzzle.print_solution()
        print(puzzle.count, "steps")
        end = time.perf_counter()
        print(round(end-start,5), "seconds")
        puzzle.draw_solution("case " + str(i+1))
    else:
        print("No solution exists.")

    print("Brute Force")
    puzzle2 = KakuroPuzzle(row_clues, col_clues, i+1)
    start = time.perf_counter()
    if puzzle2.solve_brute_force():
        print("Solution found:")
        puzzle2.print_solution()
        print(puzzle2.count, "steps")
    else:
        print("No solution exists.")
    end = time.perf_counter()
    print(round(end-start,5), "seconds")