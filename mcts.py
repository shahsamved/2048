import math
import random

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.score = 0

def mcts(root_state, iterations):
    root_node = MCTSNode(root_state)

    for _ in range(iterations):
        node = root_node
        while not node.state.get_available_moves():
            node = select_child(node)

        if not node.state.get_available_moves():
            continue

        new_state = node.state.clone()
        move = random.choice(new_state.get_available_moves())
        new_state.move(move)
        new_node = MCTSNode(new_state, parent=node)
        node.children.append(new_node)

        simulation_result = simulate(new_state)

        backpropagate(new_node, simulation_result)

    best_child = select_best_child(root_node)
    return best_child.state

def select_child(node):
    exploration_weight = 1.41  
    total_visits = sum(child.visits for child in node.children)

    uct_values = [(child.score / child.visits) + exploration_weight * math.sqrt(math.log(total_visits) / child.visits) for child in node.children]
    selected_child_index = uct_values.index(max(uct_values))
    return node.children[selected_child_index]

def simulate(state):
    max_depth = 10  
    for _ in range(max_depth):
        available_moves = state.get_available_moves()
        if not available_moves:
            break
        move = random.choice(available_moves)
        state.move(move)
    return state.get_max_tile()

def backpropagate(node, result):
    while node is not None:
        node.visits += 1
        node.score += result
        node = node.parent

def select_best_child(node):
    best_child = max(node.children, key=lambda child: child.visits)
    return best_child




