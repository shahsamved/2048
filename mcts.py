import math
import random

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.score = 0

def select(node):
    while node.children:
        node = max(node.children, key=lambda child: ucb(child))
    return node

def expand(node):
    possible_moves = node.state.get_available_moves()
    for move in possible_moves:
        new_state = node.state.clone()
        new_state.move(move)
        new_node = MCTSNode(new_state, parent=node)
        node.children.append(new_node)
    return random.choice(node.children)

def simulate(node):
    current_state = node.state.clone()
    while True:
        possible_moves = current_state.get_available_moves()
        if not possible_moves:
            break
        move = random.choice(possible_moves)
        current_state.move(move)
    return current_state.get_max_tile()

def backpropagate(node, result):
    while node:
        node.visits += 1
        node.score += result
        node = node.parent

def ucb(node):
    exploration_weight = 0.5  # Adjust as needed
    if node.visits == 0:
        return float('inf')
    return (node.score / node.visits) + exploration_weight * math.sqrt(math.log(node.parent.visits) / node.visits)
