# backend/app/saataath_ai.py
import random

# RANKS: 7 (only H/S), 8, 9, 10, J, Q, K, A
# VALUES: 7=0, 8=1 ... A=7 for comparison
SUITS = ['S', 'H', 'C', 'D']
RANK_MAP = {'7':0, '8':1, '9':2, 'T':3, 'J':4, 'Q':5, 'K':6, 'A':7}

def create_deck():
    deck = []
    for s in SUITS:
        ranks = ['8', '9', 'T', 'J', 'Q', 'K', 'A']
        if s in ['H', 'S']: ranks.insert(0, '7')
        for r in ranks:
            deck.append(r + s) # e.g., "AS", "7H"
    random.shuffle(deck)
    return deck

def get_suit(card): return card[1]
def get_rank_val(card): return RANK_MAP[card[0]]

class SaatAathGame:
    def __init__(self):
        self.deck = create_deck()
        self.hands = {0: [], 1: []} # 0=Player (Cutter), 1=Bot (Dealer)
        self.tricks_won = {0: 0, 1: 0}
        self.trump = None
        self.current_trick = [] # [(player_idx, card)]
        self.turn = 0 # Player starts (as Cutter)
        self.phase = "TRUMP_SELECT" # TRUMP_SELECT, PLAYING, FINISHED
        
        # Initial Deal (5 cards each)
        self.hands[0] = self.deck[:5]
        self.hands[1] = self.deck[5:10]
        self.deck_idx = 10

    def set_trump(self, suit):
        self.trump = suit
        # Deal remaining cards
        self.hands[0].extend(self.deck[10:20])
        self.hands[1].extend(self.deck[20:30])
        
        # Sort hands for better UX
        self.sort_hand(0)
        self.sort_hand(1)
        self.phase = "PLAYING"

    def sort_hand(self, p_idx):
        # Sort by Suit then Rank
        def sort_key(c):
            # Trump first, then standard order
            s_order = {'S':1, 'H':2, 'C':3, 'D':4}
            if self.trump: 
                s_order = {s: (0 if s == self.trump else i+1) for s,i in s_order.items()}
            return (s_order.get(c[1], 9), -get_rank_val(c))
        
        self.hands[p_idx].sort(key=sort_key)

    def play_card(self, p_idx, card_idx):
        hand = self.hands[p_idx]
        if card_idx >= len(hand): return False, "Invalid Index"
        
        card = hand[card_idx]
        
        # Validate Move
        if len(self.current_trick) > 0:
            lead_card = self.current_trick[0][1]
            lead_suit = get_suit(lead_card)
            played_suit = get_suit(card)
            
            # Must follow suit if possible
            has_suit = any(get_suit(c) == lead_suit for c in hand)
            if has_suit and played_suit != lead_suit:
                return False, f"Must follow {lead_suit}"

        # Execute
        hand.pop(card_idx)
        self.current_trick.append((p_idx, card))
        
        # Check Trick End
        if len(self.current_trick) == 2:
            self.resolve_trick()
            
        else:
            self.turn = 1 - self.turn # Switch turn
            
        return True, "OK"

    def resolve_trick(self):
        c1 = self.current_trick[0]
        c2 = self.current_trick[1]
        
        winner = self.determine_winner(c1, c2)
        self.tricks_won[winner] += 1
        self.turn = winner
        self.current_trick = [] # Clear table (frontend will handle animation delay)
        
        if len(self.hands[0]) == 0:
            self.phase = "FINISHED"

    def determine_winner(self, move1, move2):
        # move = (player_idx, card)
        p1, card1 = move1
        p2, card2 = move2
        
        s1, s2 = get_suit(card1), get_suit(card2)
        r1, r2 = get_rank_val(card1), get_rank_val(card2)
        
        # 1. Trump Logic
        if s2 == self.trump and s1 != self.trump: return p2
        if s1 == self.trump and s2 != self.trump: return p1
        
        # 2. Standard Logic
        if s1 == s2:
            return p1 if r1 > r2 else p2
            
        # 3. Discard (Lead wins if follower didn't trump)
        return p1

    def get_bot_move_idx(self):
        hand = self.hands[1]
        valid_indices = []
        
        if len(self.current_trick) == 0:
            # Leading: Pick highest non-trump or highest trump
            valid_indices = range(len(hand))
        else:
            lead_suit = get_suit(self.current_trick[0][1])
            matches = [i for i, c in enumerate(hand) if get_suit(c) == lead_suit]
            
            if matches:
                valid_indices = matches
                # Try to win?
                lead_rank = get_rank_val(self.current_trick[0][1])
                winning_moves = [i for i in matches if get_rank_val(hand[i]) > lead_rank]
                if winning_moves: return winning_moves[-1] # Lowest winning card
                return matches[0] # Throw lowest losing card
            else:
                # Trump it?
                trumps = [i for i, c in enumerate(hand) if get_suit(c) == self.trump]
                if trumps: return trumps[-1] # Lowest trump
                valid_indices = range(len(hand)) # Throw garbage

        # Fallback random valid
        return random.choice(valid_indices) if valid_indices else 0

# Store active game in memory (Simple single session for MVP)
active_game = SaatAathGame()