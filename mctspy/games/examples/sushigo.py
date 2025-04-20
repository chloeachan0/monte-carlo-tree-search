import numpy as np
from enum import Enum
from mctspy.games.common import TwoPlayersAbstractGameState, AbstractGameAction
from itertools import combinations
from random import sample
from collections import Counter
import copy 

# note: freezes when you try to use chopsticks 
class Card(Enum): 
    tempura = 1
    sashimi = 2
    dumpling = 3 
    maki2 = 4
    maki3 = 5
    maki1 = 6
    salmon_nigiri = 7
    squid_nigiri = 8
    egg_nigiri = 9
    chopsticks = 10 
    wasabi = 11
    pudding = 12

class SushiGoMove(AbstractGameAction):
    def __init__(self, chosen_card):
        # chosen card can be more than 1 card in the case of chopsticks
        self.chosen_card = chosen_card

def draw_random_cards(tot_cards): 
    card_mappings = {
    1: Card.tempura,
    2: Card.sashimi,
    3: Card.dumpling,
    4: Card.maki2,
    5: Card.maki3,
    6: Card.maki1,
    7: Card.salmon_nigiri,
    8: Card.squid_nigiri,
    9: Card.egg_nigiri,
    10: Card.chopsticks,
    11: Card.wasabi,
    12: Card.pudding,
}
    
    # draw 20 random cards, returns list or tuple of length 2, each element a list of length 10 // TODO change back to 4 * [10] 
    card_options = 14 * [1] + 14 * [2] + 14 * [3] + 12 * [4] + 8 * [5] + 6 * [6] + 10 * [7] + 5 * [8] + 5 * [9] + 10 * [12] +  6 * [11] + 10 * [10]
    twenty_cards_from_deck = sample(card_options, tot_cards)
    card_indices = sample(range(tot_cards), tot_cards)
    complete_sample = [card_mappings[twenty_cards_from_deck[i]] for i in card_indices]
    return [complete_sample[0:tot_cards//2], complete_sample[tot_cards//2:tot_cards]]

class SushiGoGameState(TwoPlayersAbstractGameState):
    def map_card(self, x):
        display_card_mapping = {
            Card.tempura: "🍤",
            Card.sashimi: "🍣",
            Card.dumpling: "🥟",
            Card.maki2: "🍱🍱",
            Card.maki3: "🍱🍱🍱",
            Card.maki1: "🍱",
            Card.salmon_nigiri: "🐟",
            Card.squid_nigiri: "🦑",
            Card.egg_nigiri: "🍳",
            Card.chopsticks: "🥢",
            Card.wasabi: "🌶️",
            Card.pudding: "🍮",
        }
        return display_card_mapping[x]

    def display_cards(self): 
        print('----------------------player 1------------------------')
        print('player 1 cards in hand: ')
        print(self.player1_cards)
        print([" " + self.map_card(x) + " " for x in self.player1_cards])
        print('\n')
        print('player 1 cards chosen: ')
        print(self.player1_cards_chosen)
        print([" " + self.map_card(x) + " " for x in self.player1_cards_chosen])
        print('-------------------------------------------------------')
        print('\n')
        print('----------------------player 2------------------------')
        print('player 2 cards in hand: ')
        print(self.player2_cards)
        print([" " + self.map_card(x) + " " for x in self.player2_cards])
        print('\n')
        print('player 2 cards chosen: ')
        print(self.player2_cards_chosen)
        print([" " + self.map_card(x) + " " for x in self.player2_cards_chosen])
        print('-------------------------------------------------------')

    player1 = 1
    player2 = 2
    def setup_cards(self): 
        player_init_cards = draw_random_cards(self.tot_cards)
        self.player1_cards = player_init_cards[0] 
        self.player2_cards = player_init_cards[1]
        self.player1_cards_chosen = []
        self.player2_cards_chosen = []

    def __init__(self, next_to_move=1, tot_cards=10):
        self.next_to_move = next_to_move
        self.num_rounds = 0
        self.player1_cur_score = 0 
        self.player2_cur_score = 0
        self.player1_puddings = 0 
        self.player2_puddings = 0 
        self.p1_score = 0 
        self.p2_score = 0
        self.p1_puddings = 0 
        self.p2_puddings = 0
        self.tot_cards = tot_cards
        self.setup_cards()
        self.display_cards()
        self.num_pass = 0
    
    def score_from_maki(self, player_card_count): 
        score = 0
        if Card.maki1 in player_card_count: 
            score += player_card_count[Card.maki1]
            player_card_count.pop(Card.maki1, None)
        if Card.maki2 in player_card_count: 
            score += 2*player_card_count[Card.maki2]
            player_card_count.pop(Card.maki2, None)
        if Card.maki3 in player_card_count: 
            score += 3*player_card_count[Card.maki3]
            player_card_count.pop(Card.maki3, None)
        return score
    
    def deal_w_wasabi(self, player_cards_chosen): 
        # returns additional score from wasabi 
        added_score = 0
        if Card.wasabi not in player_cards_chosen: 
            return 0
        wasabi_count = 0 
        score_dic = {Card.salmon_nigiri: 2, Card.egg_nigiri: 1, Card.squid_nigiri: 3}
        index = player_cards_chosen.index(Card.wasabi)
        while (index < len(player_cards_chosen)): 
            if player_cards_chosen[index] == Card.wasabi: 
                wasabi_count += 1
            elif player_cards_chosen[index] == Card.salmon_nigiri or player_cards_chosen[index] == Card.egg_nigiri or player_cards_chosen[index] == Card.squid_nigiri: 
                if wasabi_count > 0: 
                    added_score += score_dic[player_cards_chosen[index]]*2
                    wasabi_count -= 1
            index += 1
        return added_score

    def inc_score_from_cards(self, p1_score, p2_score, p1_puds, p2_puds): 
        def score_from_other_cards(item, count, playernum): 
            def dump_recursive(count): 
                if count == 1: 
                    return 1
                elif count ==2: 
                    return 3
                elif count == 3: 
                    return 6
                elif count == 4: 
                    return 10
                elif count == 5: 
                    return 15
                elif count == 6: 
                    return 21 
                else: return count+dump_recursive(count-1)

            if item == Card.tempura: 
                return (count//2)*5
            elif item == Card.sashimi: 
                return (count//3)*10
            elif item == Card.dumpling:
                return dump_recursive(count)
            elif item == Card.salmon_nigiri: 
                return count*2
            elif item == Card.egg_nigiri: 
                return count
            elif item == Card.squid_nigiri: 
                return count*3
            return 0
        p1_score += self.deal_w_wasabi(self.player1_cards_chosen)
        p2_score += self.deal_w_wasabi(self.player2_cards_chosen)

        player1_card_count = Counter(self.player1_cards_chosen)
        player2_card_count = Counter(self.player2_cards_chosen)

        player1_maki_score = self.score_from_maki(player1_card_count)
        player2_maki_score = self.score_from_maki(player2_card_count)

        if player1_maki_score > player2_maki_score: 
            p1_score += 6
            p2_score += 3
        elif player1_maki_score < player2_maki_score: 
            p1_score += 3
            p2_score += 6
        for card in set(self.player1_cards_chosen):
            if card == Card.pudding: p1_puds += player1_card_count[card]
            elif card != Card.maki1 and card != Card.maki2 and card != Card.maki3: 
                score = score_from_other_cards(card, player1_card_count[card], 1)
                p1_score += score
        for card in set(self.player2_cards_chosen): 
            if card == Card.pudding: p2_puds += player2_card_count[card]
            elif card != Card.maki1 and card != Card.maki2 and card != Card.maki3: 
                p2_score += score_from_other_cards(card, player2_card_count[card], 2)
                
        return p1_score, p2_score, p1_puds, p2_puds


    @property
    def game_result(self):
        p1_score = copy.deepcopy(self.player1_cur_score)
        p2_score = copy.deepcopy(self.player2_cur_score)
        p1_puds = copy.deepcopy(self.player1_puddings)
        p2_puds = copy.deepcopy(self.player2_puddings)

        # check if game is over
        if self.num_rounds == 2 and len(self.player2_cards_chosen) + len(self.player1_cards_chosen) == self.tot_cards: 
            p1_score, p2_score, p1_puds, p2_puds = self.inc_score_from_cards(self.player1_cur_score, self.player2_cur_score, self.player1_puddings, self.player2_puddings)

            # tally puddings
            self.p1_puddings = p1_puds
            self.p2_puddings = p2_puds
            if self.p1_puddings > self.p2_puddings: 
                p1_score += 6
                p2_score -= 6
            elif self.p1_puddings < self.p2_puddings: 
                p1_score -= 6
                p2_score += 6

            self.p1_score = p1_score 
            self.p2_score = p2_score
            if p1_score > p2_score: 
                return 1
            elif p1_score < p2_score:
                return -1 # player 2 wins
            else: 
                if self.p1_puddings == self.p2_puddings: return 0
                return 1 if self.p1_puddings > self.p2_puddings else -1
        elif len(self.player2_cards_chosen) + len(self.player1_cards_chosen) == self.tot_cards: 
            self.num_rounds += 1
            # tally cur score 
            self.player1_cur_score, self.player2_cur_score, self.player1_puddings, self.player2_puddings = self.inc_score_from_cards(p1_score, p2_score, p1_puds, p2_puds)
            self.setup_cards()

        # if not over - no result
        return None

    def is_game_over(self):
        return self.game_result is not None

    def is_move_legal(self, move):
        if move == []: 
            return False
        elif move == ['cannot move']: 
            return True
        # get cur player's deck
        cur_deck = self.player1_cards if self.next_to_move == 1 else self.player2_cards

        for card in move: 
            if card.chosen_card not in cur_deck: 
                return False
        return True 


    def move(self, move):
        if not self.is_move_legal(move):
            # we can add more info to this later maybe
            raise ValueError("your move is not legal")
        cards_to_remove = move

        game_state_cpy = copy.deepcopy(self)
        
        if cards_to_remove != [['cannot move']]: 
            chop_count = len(cards_to_remove)//2
            
            # determine cur player and remove card(s) from their deck to their 
            if self.next_to_move == self.player1:
                prev_length = len(self.player1_cards)
                for card in cards_to_remove: 
                    # print('p1 move', card.chosen_card)
                    if card != 'cannot move': 
                        game_state_cpy.player1_cards.remove(card.chosen_card)
                        game_state_cpy.player1_cards_chosen.append(card.chosen_card)
                # just makign sure the card is actually removed
                # assert(len(game_state_cpy.player2_cards) < len(self.player2_cards))
                # assert(len(game_state_cpy.player2_cards) < prev_length)

                # putting chopsticks back in hand
                for i in range(chop_count): 
                    game_state_cpy.player1_cards.append(Card.chopsticks)

                game_state_cpy.next_to_move = self.player2
            else:
                # currently player1 deck remove
                prev_length = len(self.player2_cards)
                for card in cards_to_remove: 
                    # print('p2 move', card.chosen_card)
                    if card != 'cannot move': 
                        game_state_cpy.player2_cards.remove(card.chosen_card)
                        game_state_cpy.player2_cards_chosen.append(card.chosen_card)
                # just makign sure the card is actually removed
                # assert(len(game_state_cpy.player1_cards) < len(self.player1_cards))
                # assert(len(game_state_cpy.player1_cards) < prev_length)
                
                # put chopsticks back in hand 
                for i in range(chop_count): 
                    game_state_cpy.player2_cards.append(Card.chopsticks)
                
                game_state_cpy.next_to_move = self.player1
        
        # switch decks
        if (game_state_cpy.num_pass % 2 != 0): 
            temp = game_state_cpy.player2_cards
            game_state_cpy.player2_cards = game_state_cpy.player1_cards
            game_state_cpy.player1_cards = temp 

        game_state_cpy.num_pass += 1

        return  game_state_cpy # maybe want to pass in card info here?
    
    # returns tuple satisfying (num_of_player1_cards_chosen_eq_chopsticks, num_of_player2_cards_chosen_eq_chopsticks)
    def count_chopsticks(self): 
        chop1 = 0 
        chop2 = 0 
        for card in self.player1_cards_chosen: 
            if card == Card.chopsticks: 
                chop1 += 1
        for card in self.player2_cards_chosen: 
            if card == Card.chopsticks: 
                chop2 += 1
        return (chop1, chop2)
    
    # returns List[List[SushiGoMove]] legal for the cur plater 
    def get_legal_actions(self):

        chop_p1, chop_p2 = self.count_chopsticks()

        if self.next_to_move == self.player1: #p1 turn
            actions = [SushiGoMove(c) for c in self.player1_cards]
            legal  = [[m] for m in actions] # single cards
            for k in range(chop_p1 - 1): # multi‑card w/cs (not sure this how it works)
                legal.extend([list(comb)
                                for comb in combinations(actions, 2*(k + 1))])

        else: #p2s turn
            actions = [SushiGoMove(c) for c in self.player2_cards]
            legal  = [[m] for m in actions]
            for k in range(chop_p2 - 1):
                legal.extend([list(comb)
                                for comb in combinations(actions, 2*(k + 1))])

        return legal if legal else [['cannot move']]
