import math
import time
import numpy as np
import random

UP, DOWN, LEFT, RIGHT = range(4)


class ExpectimaxAI():

    def __init__(self):
        self.total_time_taken = 0
        self.total_computation_time = 0
        self.tile_values = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
        self.scores = []
        self.move_counts = []

    def get_move(self, board):
        start_time = time.time()
        best_move, _ = self.maximize(board)
        end_time = time.time()

        time_taken = end_time - start_time
        self.total_time_taken += time_taken

        return best_move

    def eval_board(self, board, n_empty): 
        grid = board.grid

        utility = 0
        smoothness = 0

        big_t = np.sum(np.power(grid, 2))
        s_grid = np.sqrt(grid)
        smoothness -= np.sum(np.abs(s_grid[::,0] - s_grid[::,1]))
        smoothness -= np.sum(np.abs(s_grid[::,1] - s_grid[::,2]))
        smoothness -= np.sum(np.abs(s_grid[::,2] - s_grid[::,3]))
        smoothness -= np.sum(np.abs(s_grid[0,::] - s_grid[1,::]))
        smoothness -= np.sum(np.abs(s_grid[1,::] - s_grid[2,::]))
        smoothness -= np.sum(np.abs(s_grid[2,::] - s_grid[3,::]))
        
        empty_w = 100000
        smoothness_w = 3

        empty_u = n_empty * empty_w
        smooth_u = smoothness ** smoothness_w
        big_t_u = big_t

        utility += big_t
        utility += empty_u
        utility += smooth_u

        return (utility, empty_u, smooth_u, big_t_u)

    def maximize(self, board, depth = 0):
        moves = board.get_available_moves()
        moves_boards = []

        for m in moves:
            m_board = board.clone()
            m_board.move(m)
            moves_boards.append((m, m_board))

        max_utility = (float('-inf'),0,0,0)
        best_direction = None

        for mb in moves_boards:
            utility = self.chance(mb[1], depth + 1)

            if utility[0] >= max_utility[0]:
                max_utility = utility
                best_direction = mb[0]

        return best_direction, max_utility

    def chance(self, board, depth = 0):
        empty_cells = board.get_available_cells()
        n_empty = len(empty_cells)

        #if n_empty >= 7 and depth >= 5:
        #    return self.eval_board(board, n_empty)

        if n_empty >= 6 and depth >= 3:
            return self.eval_board(board, n_empty)

        if n_empty >= 0 and depth >= 5:
            return self.eval_board(board, n_empty)

        if n_empty == 0:
            _, utility = self.maximize(board, depth + 1)
            return utility

        possible_tiles = []

        chance_2 = (.9 * (1 / n_empty))
        chance_4 = (.1 * (1 / n_empty))
        
        for empty_cell in empty_cells:
            possible_tiles.append((empty_cell, 2, chance_2))
            possible_tiles.append((empty_cell, 4, chance_4))

        utility_sum = [0, 0, 0, 0]

        for t in possible_tiles:
            t_board = board.clone()
            t_board.insert_tile(t[0], t[1])
            _, utility = self.maximize(t_board, depth + 1)

            for i in range(4):
                utility_sum[i] += utility[i] * t[2]

        return tuple(utility_sum)
    

    def evaluate_strategy(self, board, num_games=10):
        for game_num in range(1, num_games + 1):
            print(f"Starting Game {game_num}")
            start_time = time.time()
            game_board = board.clone()
            total_moves = 0

            while len(game_board.get_available_moves()) > 0:
                move = self.get_move(game_board)
                total_moves += 1
                game_board.move(move)

            end_time = time.time()

            max_tile = game_board.get_max_tile()
            total_score = max_tile

            print(f"Game {game_num} - Final Score: {total_score}, Total Moves: {total_moves}")
            print(f"Game {game_num} - Final Board:")
            print(game_board)

            self.total_computation_time += end_time - start_time

            self.scores.append(total_score)
            self.move_counts.append(total_moves)

        self.print_metrics()

    def print_metrics(self):
        print("Strategy Evaluation Metrics:")
        print(f"Time Taken: {self.total_time_taken} seconds")
        print(f"Computation Time: {self.total_computation_time} seconds")
        print(f"Tile Values: {self.tile_values}")
        print("\nPerformance Metrics:")
        print(f"Average Score: {np.mean(self.scores)}")
        print(f"Median Score: {np.median(self.scores)}")
        print(f"Average Move Count: {np.mean(self.move_counts)}")
        print(f"Median Moves: {np.median(self.move_counts)}")
    
    # def mcts(self, board, iterations=1000):
    #     root = MCTSNode(board.clone())

    #     for _ in range(iterations):
    #         selected_node = select(root)
    #         expanded_node = expand(selected_node)
    #         simulation_result = simulate(expanded_node)
    #         backpropagate(expanded_node, simulation_result)

    #     best_child = max(root.children, key=lambda child: child.visits)
    #     return best_child.state
