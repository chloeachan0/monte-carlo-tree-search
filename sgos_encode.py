# TENSOR FOR GAME STATE
import numpy as np
from mctspy.games.examples.sushigo import Card, SushiGoGameState

N_CARDS = len(Card)  # 12
HAND_SIZE = 10  # max cards in hand early game


def encode_state(state: SushiGoGameState) -> np.ndarray:
    """
    One-hot / count encoding.
      [ player1 tableau counts (12) |
        player2 tableau counts (12) |
        player1 hand counts   (12) |
        player2 hand counts   (12) |
        player1 score (1) |
        player2 score (1) |
        player1 puddings (1) |
        player2 puddings (1) |
        round (1) |
        to_move (1—P1=0,P2=1) ]
    → 54-dim vector
    """
    vec = np.zeros(54, dtype=np.float32)

    def add_counts(offset, cards):
        for c in cards:
            vec[offset + (c.value - 1)] += 1  # Enum values start at 1

    add_counts(0, state.player1_cards_chosen)
    add_counts(12, state.player2_cards_chosen)
    add_counts(24, state.player1_cards)
    add_counts(36, state.player2_cards)

    vec[48] = state.player1_cur_score
    vec[49] = state.player2_cur_score
    vec[50] = state.player1_puddings
    vec[51] = state.player2_puddings
    vec[52] = state.num_rounds  # 0,1,2
    vec[53] = 0 if state.next_to_move == 1 else 1

    # no idea if this needs to be scaled lol
    return vec
