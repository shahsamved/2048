from tkinter import Frame, Label, CENTER
from tkinter import StringVar
from tkinter import OptionMenu
import threading



from random import randint
import time

from game_board import GameBoard
# from ai import AI
from expectimax import ExpectimaxAI
from mcts import MCTSNode,mcts
from Qlearning import DQNAgent


SIZE = 500
GRID_LEN = 4
GRID_PADDING = 10

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_CELL_EMPTY = "#9e948a"
BACKGROUND_COLOR_DICT = {   2:"#eee4da", 4:"#ede0c8", 8:"#f2b179", 16:"#f59563", \
                            32:"#f67c5f", 64:"#f65e3b", 128:"#edcf72", 256:"#edcc61", \
                            512:"#edc850", 1024:"#edc53f", 2048:"#edc22e" }
CELL_COLOR_DICT = { 2:"#776e65", 4:"#776e65", 8:"#f9f6f2", 16:"#f9f6f2", \
                    32:"#f9f6f2", 64:"#f9f6f2", 128:"#f9f6f2", 256:"#f9f6f2", \
                    512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2" }
FONT = ("Verdana", 40, "bold")

class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        self.grid_cells = []

        self.init_grid()
        self.init_matrix()
        self.update_grid_cells()
        # self.AI = AI()
        self.total_time_taken = 0
        self.Expectimax = ExpectimaxAI()
        # self.MCTS = MCTSNode()
        self.MCTS = MCTSNode(state=self.board.clone())
        self.dqn_agent = DQNAgent(16, 4)

        self.algorithm_var = StringVar(self)
        self.algorithm_var.set("mcts")  # Default algorithm
        algorithm_menu = OptionMenu(self, self.algorithm_var, "expectimax","mcts","dqn")
        algorithm_menu.grid(row=0, column=5, padx=10, pady=10)

        self.run_game()
        self.mainloop()
    
    # def run_mcts(self):
    #     iterations = 1 
    #     self.board = mcts(self.board, iterations)

    def run_mcts(self):
        iterations = 1000  # You can adjust the number of iterations
        final_state = mcts(self.board, iterations)
        self.board = final_state
        self.update_grid_cells()

    def run_game(self):
        while True:
            move_algorithm = self.algorithm_var.get()
            if move_algorithm == "mcts":
                start_time = time.time()
                self.board.move(self.Expectimax.get_move(self.board))
                end_time = time.time()
                self.total_time_taken += end_time - start_time
    
            elif move_algorithm == "mcts":
                self.run_mcts()
            elif move_algorithm == "dqn":
                self.board.move(self.dqn_agent.get_action(self.board))
            else:
                raise ValueError("Invalid algorithm selected")
            # self.board.move(self.Expectimax.get_move(self.board))
            self.update_grid_cells()
            self.add_random_tile()
            self.update_grid_cells()

            if len(self.board.get_available_moves()) == 0:
                self.game_over_display()
                break

            self.update()
    def print_strategy_metrics(self):
        self.Expectimax.evaluate_strategy(self.board, num_games=10)
        self.Expectimax.print_metrics()
        
    def game_over_display(self):
        for i in range(4):
            for j in range(4):
                self.grid_cells[i][j].configure(text="", bg=BACKGROUND_COLOR_CELL_EMPTY)

        self.grid_cells[1][1].configure(text="TOP",bg=BACKGROUND_COLOR_CELL_EMPTY)
        self.grid_cells[1][2].configure(text="4 TILES:",bg=BACKGROUND_COLOR_CELL_EMPTY)
        top_4 = list(map(int, reversed(sorted(list(self.board.grid.flatten())))))
        self.grid_cells[2][0].configure(text=str(top_4[0]), bg=BACKGROUND_COLOR_DICT[2048], fg=CELL_COLOR_DICT[2048])
        self.grid_cells[2][1].configure(text=str(top_4[1]), bg=BACKGROUND_COLOR_DICT[2048], fg=CELL_COLOR_DICT[2048])
        self.grid_cells[2][2].configure(text=str(top_4[2]), bg=BACKGROUND_COLOR_DICT[2048], fg=CELL_COLOR_DICT[2048])
        self.grid_cells[2][3].configure(text=str(top_4[3]), bg=BACKGROUND_COLOR_DICT[2048], fg=CELL_COLOR_DICT[2048])
        self.update()

    def init_grid(self):
        background = Frame(self, bg=BACKGROUND_COLOR_GAME, width=SIZE, height=SIZE)
        background.grid()

        for i in range(GRID_LEN):
            grid_row = []

            for j in range(GRID_LEN):

                cell = Frame(background, bg=BACKGROUND_COLOR_CELL_EMPTY, width=SIZE/GRID_LEN, height=SIZE/GRID_LEN)
                cell.grid(row=i, column=j, padx=GRID_PADDING, pady=GRID_PADDING)
                # font = Font(size=FONT_SIZE, family=FONT_FAMILY, weight=FONT_WEIGHT)
                t = Label(master=cell, text="", bg=BACKGROUND_COLOR_CELL_EMPTY, justify=CENTER, font=FONT, width=4, height=2)
                t.grid()
                grid_row.append(t)

            self.grid_cells.append(grid_row)

    def gen(self):
        return randint(0, GRID_LEN - 1)

    def init_matrix(self):
        self.board = GameBoard()
        self.add_random_tile()
        self.add_random_tile()

    def update_grid_cells(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                new_number = int(self.board.grid[i][j])
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    n = new_number
                    if new_number > 2048:
                        c = 2048
                    else:
                        c = new_number

                    self.grid_cells[i][j].configure(text=str(n), bg=BACKGROUND_COLOR_DICT[c], fg=CELL_COLOR_DICT[c])
        self.update_idletasks()
        
    def add_random_tile(self):
        if randint(0,99) < 100 * 0.9:
            value = 2
        else:
            value = 4

        cells = self.board.get_available_cells()
        pos = cells[randint(0, len(cells) - 1)] if cells else None

        if pos is None:
            return None
        else:
            self.board.insert_tile(pos, value)
            return pos

gamegrid = GameGrid()
gamegrid.print_strategy_metrics()