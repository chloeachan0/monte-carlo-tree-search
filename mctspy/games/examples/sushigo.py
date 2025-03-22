import numpy as np
from enum import Enum
from mctspy.games.common import TwoPlayersAbstractGameState, AbstractGameAction
from itertools import combinations
from random import sample
from collections import Counter
import copy 

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
    
    # draw 20 random cards, returns list or tuple of length 2, each element a list of length 10
    card_options = 14 * [1] + 14 * [2] + 14 * [3] + 12 * [4] + 8 * [5] + 6 * [6] + 10 * [7] + 5 * [8] + 5 * [9] + 10 * [10] + 6 *[11] + 4 * [12]
    twenty_cards_from_deck = sample(card_options, tot_cards)
    card_indices = sample(range(tot_cards), tot_cards)
    complete_sample = [card_mappings[twenty_cards_from_deck[i]] for i in card_indices]

    # print('player 1 init cards', complete_sample[0:11])
    # print('player 2 init cards', complete_sample[11:20])
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

    def __init__(self, next_to_move=1, tot_cards=4):
        #print('new game')
        self.next_to_move = next_to_move
        self.num_rounds = 1
        self.player1_cur_score = 0 
        self.player2_cur_score = 0
        self.player1_puddings = 0 
        self.player2_puddings = 0 
        self.tot_cards = tot_cards
        self.setup_cards()
        self.display_cards()
        self.num_pass = 0
        # possibly change next to move to initially be random

    
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
        # print('make sure player card count does not include makis')
        # print(player_card_count)
        return score
    
    def deal_w_wasabi(self, player_cards_chosen): 
        index = 0 
        # indices to exclude of wasabi and corresponding nigiri 
        excluded_indices = []

        def get_remaining_cards(): 
            remaining = []
            for i in range(len(player_cards_chosen)): 
                if i != excluded_indices: 
                    remaining.append(player_cards_chosen[i])
            return remaining
        while index < len(player_cards_chosen): 
            if player_cards_chosen[index] == Card.wasabi: 
                # find nigiri 
                salmon_nigiri_idx = player_cards_chosen.index(Card.salmon_nigiri) if Card.salmon_nigiri in player_cards_chosen else -1
                squid_nigiri_idx = player_cards_chosen.index(Card.squid_nigiri) if Card.squid_nigiri in player_cards_chosen else -1
                egg_nigiri_idx = player_cards_chosen.index(Card.egg_nigiri) if Card.egg_nigiri in player_cards_chosen else -1
                if max(salmon_nigiri_idx, squid_nigiri_idx, egg_nigiri_idx) < index:
                    if excluded_indices == []: return player_cards_chosen
                    return get_remaining_cards()
                after_wasabi = []
                if salmon_nigiri_idx > index: 
                    after_wasabi.append(salmon_nigiri_idx)
                if squid_nigiri_idx > index: 
                    after_wasabi.append(squid_nigiri_idx)
                if egg_nigiri_idx > index: 
                    after_wasabi.append(egg_nigiri_idx)
                closest_index = min(after_wasabi)
                excluded_indices.append(index)
                excluded_indices.append(closest_index)
                index = closest_index
            index += 1
        return get_remaining_cards()

    def inc_score_from_cards(self): 
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
    
        player1_card_count = Counter(self.deal_w_wasabi(self.player1_cards_chosen))
        player2_card_count = Counter(self.deal_w_wasabi(self.player2_cards_chosen))

        player1_maki_score = self.score_from_maki(player1_card_count)
        player2_maki_score = self.score_from_maki(player2_card_count)

        if player1_maki_score > player2_maki_score: 
            self.player1_cur_score += 6
            self.player2_cur_score += 3
        elif player1_maki_score < player2_maki_score: 
            self.player1_cur_score += 3
            self.player2_cur_score += 6
        
        for card in self.player1_cards_chosen: 
            if card == Card.pudding: self.player1_puddings += player1_card_count[card]
            else: self.player1_cur_score += score_from_other_cards(card, player1_card_count[card], 1)
        for card in self.player2_cards_chosen: 
            if card == Card.pudding: self.player2_puddings += player2_card_count[card]
            else: self.player2_cur_score += score_from_other_cards(card, player2_card_count[card], 2)



    @property
    def game_result(self):
        print('length of cards chosen: ', len(self.player1_cards_chosen), len(self.player2_cards_chosen), self.tot_cards)
        # check if game is over
        if self.num_rounds == 3: 
            self.inc_score_from_cards()
            # tally puddings
            if self.player1_puddings > self.player2_puddings: 
                self.player1_cur_score += 6
                self.player2_cur_score -= 6
            elif self.player1_puddings < self.player2_puddings: 
                self.player1_cur_score -= 6
                self.player2_cur_score += 6
            
            print('final scores: ')
            print('player 1: ', self.player1_cur_score)
            print('player 2', self.player2_cur_score)
            
            # TODO need to reset num of rounds self.num_rounds -= 1
            # exit()
            # can add exit() here to get scores from one round
            # determine winner from final score
            if self.player1_cur_score > self.player2_cur_score: 
                return 1
            elif self.player1_cur_score < self.player2_cur_score: 
                return -1 # player 2 wins
            else: 
                if self.player1_puddings == self.player2_puddings: return 0
                return 1 if self.player1_puddings > self.player2_puddings else -1
        elif len(self.player2_cards_chosen) + len(self.player1_cards_chosen) == self.tot_cards: 
            # increment rounds and reset cards 
            self.num_rounds += 1
            # tally cur score 
            self.inc_score_from_cards()
            print('score from ')
            print('player 1 score', self.player1_cur_score)
            print('player 2 score', self.player2_cur_score)
            # reset cards
            print('end of round.')
            self.setup_cards()
        print('check game res')
        self.display_cards()
        print('num rounds', self.num_rounds)
        
        # if not over - no result
        return None

    def is_game_over(self):
        return self.game_result is not None

    def is_move_legal(self, move):
        if move == []: 
            return False
        # check if correct player moves --> need to figure out appropriate way for this
        # if move.value != self.next_to_move:
        #     return False
        
        # get cur player's deck
        cur_deck = self.player1_cards
        if self.next_to_move == 1: 
            cur_deck = self.player2_cards
        # assert(len(move) == 1)

        # check if player chooses card from their deck 
        print('move', move)
        for card in move: 
            print('card chosen', card.chosen_card)
            # if type(card) == list: 
            #     for item in card: 
            #         # print('item we chose (list?): ', item.chosen_card)
            #         if item.chosen_card not in cur_deck: 
            #             print('we chose a card not in deck')
            #             return False
            if card.chosen_card not in cur_deck: 
                print('we chose a card not in deck')
                return False
        return True 


    def move(self, move):
        print('move!')
        if not self.is_move_legal(move):
            # we can add more info to this later maybe
            raise ValueError("your move is not legal")
        print(type(move))
        for x in move: 
            print('x is ', x)
            # print('chosen card: ', x.chosen_card)
        cards_to_remove = move
        print(type(cards_to_remove))

        game_state_cpy = copy.deepcopy(self)
        # determine cur player and remove card(s) from their deck to their 
        if self.next_to_move == self.player1:
            # currently player2 deck remove
            prev_length = len(self.player2_cards)
            for card in cards_to_remove: 
                game_state_cpy.player2_cards.remove(card.chosen_card)
                game_state_cpy.player2_cards_chosen.append(card.chosen_card)
            # just makign sure the card is actually removed
            assert(len(game_state_cpy.player2_cards) < prev_length)

            # putting chopsticks back in hand
            for i in range(int(len(cards_to_remove)/2)): 
                game_state_cpy.player2_cards.append(Card.chopsticks)

            game_state_cpy.next_to_move = self.player2
        else:
            # currently player1 deck remove
            prev_length = len(self.player1_cards)
            for card in cards_to_remove: 
                game_state_cpy.player1_cards.remove(card.chosen_card)
                game_state_cpy.player1_cards_chosen.append(card.chosen_card)
            # just makign sure the card is actually removed
            assert(len(game_state_cpy.player1_cards) < prev_length)
            
            # put chopsticks back in hand 
            for i in range(int(len(cards_to_remove)/2)): 
                game_state_cpy .player1_cards.append(Card.chopsticks)
            
            game_state_cpy.next_to_move = self.player1
        
        # switch decks
        if (game_state_cpy.num_pass % 2 != 0): 
            temp = game_state_cpy.player2_cards
            game_state_cpy.player2_cards = game_state_cpy.player1_cards
            game_state_cpy.player1_cards = temp 
            print('after removal:')
            game_state_cpy.display_cards()
        game_state_cpy.num_pass += 1
        # never move onto second round? 
        # if (self.num_pass == 2): 
        #     exit()
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
    
    def get_legal_actions(self):
        # chopstick count to determine possible legal actions
        chop_count = self.count_chopsticks()

        if self.next_to_move == self.player1: 
            print(f'legal actions for player {self.player2}')
            # player 2 
            # legal_actions = []
            actions = [SushiGoMove(card) for card in self.player2_cards]
            legal_actions = [[SushiGoMove(card)] for card in self.player2_cards]
            for i in range(chop_count[1]): 
               legal_actions.extend([list(comb) for comb in combinations(actions, 2*(i+1))])     
        else: 
            print(f'legal actions for player {self.player1}')
            # player 1
            actions = [SushiGoMove(card) for card in self.player1_cards]
            legal_actions = [[SushiGoMove(card)] for card in self.player1_cards]
            for i in range(chop_count[0]): 
                legal_actions.extend([list(comb) for comb in combinations(actions, 2*(i+1))])
        print('length of legal actions', len(legal_actions))
        possible_choices = []
        possible_choices1 = []
        for x in legal_actions: 
            action_lst = []
            action_lst1 = []
            for item in x: 
                action_lst1.append(self.map_card(item.chosen_card)) # will not work when item can be a list of two cards
                action_lst.append(item.chosen_card)
            possible_choices.append(action_lst)
            possible_choices1.append(action_lst1)
        print(possible_choices)
        print(possible_choices1)
        return legal_actions