# 🍣 AI Bot for Sushi Go!

[**Sushi Go!**](https://gamewright.com/product/Sushi-Go) is a fast-paced card drafting game designed by Harding and published by Gamewright. The theme of the game is based on conveyor belt sushi restaurants where players can pick different sushi dishes and create meals to gain points. The goal is to acquire the best sushi dishes while preventing your opponents from out-ordering you. The game has 3 rounds and in each round, players are dealt a hand of 9 cards. The player with the most points at the end wins! 

You play as **Player 1** against an AI that combines Monte-Carlo Tree Search and a small neural value‐network.  
After a few self-play training loops the bot routinely beats expert-level humans.

---

## Table of Contents
1. [Quick start – Play now!](#quick-start--play-now)
2. [Prerequisites](#prerequisites)
3. [Generate your own self-play dataset](#generate-your-own-self-play-dataset)
4. [Train the value network](#train-the-value-network)

---

## Quick start – Play now! <a name="quick-start--play-now"></a>

```bash

python -m venv sg_env
source sg_env/bin/activate # Windows: sg_env\Scripts\activate
pip install -r requirements.txt

python gui_botVN.py
```

## Prerequisites
| Requirement | Version / Notes |
|-------------|-----------------|
| **Python**  | 3.9 – 3.12 |
| **PyTorch** | 2.x  |
| **NumPy**, **tqdm**, **mctspy**, **Tkinter** |  |

## Generate your own self-play dataset <a name="generate-your-own-self-play-dataset"></a>

1. in gen_selfplay.py, choose how many games and think-time per move you want:

   ```bash
   # Example: 10 000 games, 0.05 s MCTS/ply, using every CPU core –  ≈ 13 minutes (Ryzen 9 5900HX)
   python gen_selfplay.py --games 10000 --sim-sec 0.05
   ```
2. Result will be stored as (54-float vector, final winner) tuples in selfplay_xg_ys.pkl

## Train the value network <a name="train-the-value-network"></a>

1. In train_value.py:

  ```bash
  python train_value.py --data selfplay_10000g_0.05s.pkl --epochs 25
  ```

default architecture for this project is 54 -> 256 -> 128 -> 1 with tanh output

2. new model autoloaded by gui_botVN.

## Iterate

Future datasets evaluate all leaves by the newly trained net. Merge/replace datasets, and re-train.
