# mcts_val.py
import torch, torch.nn as nn
from sgos_encode import encode_state
from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from train_value import ValueNet


class ValueNetWrapper:
    "Loads the net once and keeps it on GPU/CPU."

    def __init__(self, path="value_net.pt", device="cpu"):
        self.net = ValueNet().to(device)
        self.net.load_state_dict(torch.load(path, map_location=device))
        self.net.eval()
        self.device = device

    def value(self, state):
        x = torch.tensor(
            encode_state(state)[None, :], dtype=torch.float32, device=self.device
        )
        with torch.no_grad():
            return float(self.net(x).item())  # scalar ∈ (-1,1)


VNET = ValueNetWrapper(device="cuda" if torch.cuda.is_available() else "cpu")


class ValuedNode(TwoPlayersGameMonteCarloTreeSearchNode):
    def evaluate(self, state):  # called when expanding a new leaf
        return VNET.value(state)  # instead of rollout()
