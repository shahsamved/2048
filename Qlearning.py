import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from game_board import GameBoard

class QNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

class DQNAgent:
    def __init__(self, input_size, output_size, learning_rate=0.001, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.995):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = QNetwork(input_size, output_size).to(self.device)
        self.target_q_network = QNetwork(input_size, output_size).to(self.device)
        self.target_q_network.load_state_dict(self.q_network.state_dict())
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay

    def get_state_tensor(self, board):
        # Convert the board state to a PyTorch tensor
        return torch.FloatTensor(board.grid.flatten()).to(self.device)

    def get_action(self, board):
        state = self.get_state_tensor(board)
        
        # Explore with probability epsilon
        if np.random.rand() < self.exploration_rate:
            return np.random.choice(board.get_available_moves())
        
        # Exploit by choosing the action with the highest Q-value
        with torch.no_grad():
            q_values = self.q_network(state)
        return int(torch.argmax(q_values))

    def update_q_values(self, state, action, reward, next_state, done):
        state_tensor = self.get_state_tensor(state)
        next_state_tensor = self.get_state_tensor(next_state)

        with torch.no_grad():
            if done:
                target_q_value = reward
            else:
                target_q_values = self.target_q_network(next_state_tensor)
                target_q_value = reward + self.discount_factor * torch.max(target_q_values).item()

        predicted_q_values = self.q_network(state_tensor)
        predicted_q_value = predicted_q_values[action]

        loss = self.loss_fn(predicted_q_value, torch.tensor(target_q_value).to(self.device))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def train(self, board, num_episodes=1000):
        input_size = len(board.grid.flatten())
        output_size = len(board.get_available_moves())

        for episode in range(num_episodes):
            state = board.clone()
            total_reward = 0

            while True:
                action = self.get_action(state)
                next_state = state.clone()
                moved = next_state.move(action, get_avail_call=True)

                if not moved:
                    # Invalid move, penalize the agent
                    reward = -1
                else:
                    reward = next_state.get_max_tile()

                self.update_q_values(state, action, reward, next_state, len(next_state.get_available_moves()) == 0)

                total_reward += reward
                state = next_state

                if len(state.get_available_moves()) == 0:
                    # Game over, break out of the loop
                    break

            # Decay exploration rate
            self.exploration_rate *= self.exploration_decay

            print(f"Episode: {episode + 1}, Total Reward: {total_reward}")

if __name__ == "__main__":
    input_size = len(GameBoard().grid.flatten())
    output_size = len(GameBoard().get_available_moves())

    dqn_agent = DQNAgent(input_size, output_size)
    game_board = GameBoard()
    dqn_agent.train(game_board, num_episodes=1000)
    
