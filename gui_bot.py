
import tkinter as tk
from tkinter import messagebox
from mctspy.games.examples.sushigo import SushiGoGameState, SushiGoMove
from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
import datetime
import json

class SushiGoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🍣 Sushi Go! 🍣")
        self.configure(bg="#f7f4e9")
        self.state = SushiGoGameState()
        self.selected_indices = set()
        self.card_buttons = []
        self.stats = {
            "rounds": [],
            "final_scores": {},
            "winner": None
        }
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # Header
        header_frame = tk.Frame(self, bg="#f7f4e9")
        header_frame.pack(pady=10)
        header = f"Round {self.state.num_rounds}   P1: {self.state.player1_cur_score} | P2: {self.state.player2_cur_score}"
        tk.Label(header_frame, text=header, font=("Helvetica", 16, "bold"), bg="#f7f4e9").pack()

        current_player = "Player 1" if self.state.next_to_move == 1 else "AI Bot (Player 2)"
        tk.Label(header_frame, text=f"{current_player}'s Turn", font=("Helvetica", 14), fg="red", bg="#f7f4e9").pack()

        # Cards in hand
        hand_frame = tk.Frame(self, bg="#f7f4e9")
        hand_frame.pack(pady=10)
        self.card_buttons.clear()
        hand = self.state.player1_cards if self.state.next_to_move == 1 else self.state.player2_cards

        for idx, card in enumerate(hand):
            emoji = self.state.map_card(card)
            btn = tk.Button(
                hand_frame, text=emoji, font=("Arial", 32), width=3, height=2,
                bg="#ffffff", activebackground="#ffebcd",
                command=lambda i=idx: self._toggle_card_selection(i)
            )
            btn.grid(row=0, column=idx, padx=5)
            self.card_buttons.append(btn)

        # Selected card label
        self.selected_label = tk.Label(self, text="Selected: None", font=("Helvetica", 12), bg="#f7f4e9")
        self.selected_label.pack(pady=5)

        # Play button
        if self.state.next_to_move == 1:
            play_btn = tk.Button(self, text="Play Selected Cards", font=("Helvetica", 14), bg="#d3f8e2", command=self._submit_move)
            play_btn.pack(pady=10)

        # Played cards so far
        self._show_played_cards()

        # If bot's turn, schedule next move
        if self.state.next_to_move == 2:
            self.after(1000, self._make_ai_move)

    def _toggle_card_selection(self, idx):
        if idx in self.selected_indices:
            self.selected_indices.remove(idx)
            self.card_buttons[idx].config(bg="#ffffff")
        else:
            self.selected_indices.add(idx)
            self.card_buttons[idx].config(bg="#ccffcc")

        hand = self.state.player1_cards
        selected_emojis = [self.state.map_card(hand[i]) for i in self.selected_indices]
        self.selected_label.config(text="Selected: " + " ".join(selected_emojis) if selected_emojis else "Selected: None")

    def _submit_move(self):
        hand = self.state.player1_cards
        selected = [SushiGoMove(hand[i]) for i in self.selected_indices]

        if not selected:
            messagebox.showwarning("No Cards", "Please select at least one card.")
            return

        try:
            self.state = self.state.move(selected)
        except ValueError as err:
            messagebox.showerror("Illegal Move", str(err))
            return

        self.selected_indices.clear()
        self._handle_game_progress()

    def _make_ai_move(self):
      try:
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=self.state)
        mcts  = MonteCarloTreeSearch(root)

        # search for one secs
        best_node = mcts.best_action(total_simulation_seconds=1)

        self.state = best_node.state

      except Exception as exc:
        messagebox.showerror("AI Error", f"AI turn failed:\n{exc}")
        return

      self._handle_game_progress()

    def _handle_game_progress(self):
        if self.state.is_game_over():
            res = self.state.game_result
            msg = "It's a tie!" if res == 0 else ("Player 1 wins!" if res == 1 else "AI Bot (Player 2) wins!")
            self.stats["final_scores"] = {
                "Player 1": self.state.player1_cur_score,
                "Player 2": self.state.player2_cur_score
            }
            self.stats["winner"] = msg
            messagebox.showinfo("Game Over", msg)
            self._save_game_stats()
            self.destroy()
        else:
            self._build_ui()

    def _show_played_cards(self):
        chosen_frame = tk.Frame(self, bg="#f7f4e9")
        chosen_frame.pack(pady=10)

        tk.Label(chosen_frame, text="Played Cards", font=("Helvetica", 12, "bold"), bg="#f7f4e9").pack()

        for player, cards in [("Player 1", self.state.player1_cards_chosen), ("AI Bot", self.state.player2_cards_chosen)]:
            frame = tk.Frame(chosen_frame, bg="#f7f4e9")
            frame.pack()
            emojis = " ".join(self.state.map_card(c) for c in cards)
            tk.Label(frame, text=f"{player}: {emojis}", font=("Helvetica", 12), bg="#f7f4e9").pack()

    def _save_game_stats(self):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sushigo_stats_{now}.json"
        with open(filename, "w") as f:
            json.dump(self.stats, f, indent=4)
        print(f"Game stats saved to {filename}")

if __name__ == "__main__":
    app = SushiGoGUI()
    app.mainloop()
