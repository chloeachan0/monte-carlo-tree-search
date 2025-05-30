import numpy as np
from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.examples.tictactoe import TicTacToeGameState
from mctspy.games.examples.sushigo import SushiGoGameState
import sys, os

if __name__ == "__main__": 
    # disable print statements
    #sys.stdout = open(os.devnull, 'w')
    state = SushiGoGameState(next_to_move=1, tot_cards=10)
    count = 0 
    # assert tot cards = even
    while state.game_result is None:
        # calculate best move
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=state,
                                                  parent=None)
        mcts = MonteCarloTreeSearch(root)
        best_node = mcts.best_action(total_simulation_seconds=1)

        state = best_node.state
        print(state.display_cards())
        
    print('player 1 final score', state.p1_score)
    print('player 2 final score', state.p2_score)
 