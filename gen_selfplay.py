# try multiprocessing
import pickle, random, tqdm, os, multiprocessing as mp
from sgos_encode import encode_state
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.examples.sushigo import SushiGoGameState
from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode as BaseNode

GAMES = 10_000
SIM_SEC = 0.05  # per move
N_PROC = mp.cpu_count() - 1  # leave one core free


def play_one(seed: int):
    random.seed(seed)  # make games reproducible
    s = SushiGoGameState(next_to_move=random.choice([1, 2]))
    trajectory = []

    while not s.is_game_over():
        root = BaseNode(state=s)
        best = MonteCarloTreeSearch(root).best_action(total_simulation_seconds=SIM_SEC)
        trajectory.append(encode_state(s))  # keep feature only
        s = best.state

    z = s.game_result  # 1 / 0 / -1
    return [(vec, z) for vec in trajectory]  # tag every state


def main():
    with mp.Pool(N_PROC) as pool:
        seeds = list(range(GAMES))
        all_records = []
        for game_records in tqdm.tqdm(
            pool.imap_unordered(play_one, seeds), total=GAMES
        ):
            all_records.extend(game_records)

    fname = f"selfplay_{GAMES}g_{SIM_SEC:.2f}s.pkl"
    with open(fname, "wb") as f:
        pickle.dump(all_records, f)
    print("saved", fname, "positions:", len(all_records))


if __name__ == "__main__":
    # Windows requires the “spawn” start method for CUDA / torch
    if os.name == "nt":
        mp.set_start_method("spawn")
    main()
