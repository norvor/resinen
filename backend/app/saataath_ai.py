import random

# --- GAME CONFIG ---
SUITS = ['S', 'H', 'C', 'D']
RANK_MAP = {'7':0, '8':1, '9':2, 'T':3, 'J':4, 'Q':5, 'K':6, 'A':7}

def create_deck():
    deck = []
    for s in SUITS:
        ranks = ['8', '9', 'T', 'J', 'Q', 'K', 'A']
        if s in ['H', 'S']: ranks.insert(0, '7')
        for r in ranks:
            deck.append(r + s)
    random.shuffle(deck)
    return deck

def get_suit(card): return card[1]
def get_rank_val(card): return RANK_MAP[card[0]]

class SaatAathGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.deck = create_deck()
        self.hands = {0: [], 1: []} # 0=Player, 1=Bot
        self.tricks_won = {0: 0, 1: 0}
        self.trump = None
        self.current_trick = [] 
        self.last_trick = None
        self.last_winner = None
        self.turn = 0 
        self.phase = "TRUMP_SELECT"
        
        # Initial Deal (5 cards)
        self.hands[0] = sorted(self.deck[:5], key=lambda c: (c[1], -get_rank_val(c)))
        self.hands[1] = self.deck[5:10]

    def set_trump(self, suit):
        self.trump = suit
        # Second Deal (Rest of cards)
        self.hands[0].extend(self.deck[10:20])
        self.hands[1].extend(self.deck[20:30])
        
        self.sort_hand(0)
        self.sort_hand(1)
        self.phase = "PLAYING"

    def sort_hand(self, p_idx):
        def sort_key(c):
            s_order = {'S':1, 'H':2, 'C':3, 'D':4}
            s_val = 0 if c[1] == self.trump else s_order.get(c[1], 9)
            return (s_val, -get_rank_val(c))
        self.hands[p_idx].sort(key=sort_key)

    def play_card(self, p_idx, card):
        """
        Accepts 'card' string (e.g. "7H") to avoid index errors.
        """
        if self.phase == "FINISHED": return False, "Game Over"
        
        hand = self.hands[p_idx]
        
        # 1. Validation
        if card not in hand:
            return False, "Card not in hand"
            
        # 2. Rule Check: Must Follow Suit
        if len(self.current_trick) > 0:
            lead_card = self.current_trick[0][1]
            lead_suit = get_suit(lead_card)
            played_suit = get_suit(card)
            
            has_suit = any(get_suit(c) == lead_suit for c in hand)
            
            if has_suit and played_suit != lead_suit:
                return False, f"You must play {lead_suit}"

        # 3. Execute
        hand.remove(card)
        self.current_trick.append((p_idx, card))
        
        # Check Trick End
        if len(self.current_trick) == 2:
            self.resolve_trick()
        else:
            self.turn = 1 - self.turn 
            
        return True, "OK"

    def resolve_trick(self):
        c1 = self.current_trick[0]
        c2 = self.current_trick[1]
        
        winner = self.determine_winner(c1, c2)
        self.tricks_won[winner] += 1
        self.turn = winner
        
        # Save state for UI animation
        self.last_trick = list(self.current_trick)
        self.last_winner = winner
        self.current_trick = [] 
        
        if len(self.hands[0]) == 0:
            self.phase = "FINISHED"

    def determine_winner(self, move1, move2):
        p1, card1 = move1
        p2, card2 = move2
        
        s1, s2 = get_suit(card1), get_suit(card2)
        r1, r2 = get_rank_val(card1), get_rank_val(card2)
        
        if s2 == self.trump and s1 != self.trump: return p2
        if s1 == self.trump and s2 != self.trump: return p1
        
        if s1 == s2:
            return p1 if r1 > r2 else p2
            
        return p1

    def get_bot_move_card(self):
        """
        Returns the CARD STRING to play.
        """
        try:
            hand = self.hands[1]
            if not hand: return None
            
            chosen_idx = 0
            
            # LOGIC
            if len(self.current_trick) == 0:
                # Leading: Play highest rank
                chosen_idx = max(range(len(hand)), key=lambda i: get_rank_val(hand[i]))
            else:
                # Following
                lead_suit = get_suit(self.current_trick[0][1])
                matches = [i for i, c in enumerate(hand) if get_suit(c) == lead_suit]
                
                if matches:
                    lead_rank = get_rank_val(self.current_trick[0][1])
                    winning = [i for i in matches if get_rank_val(hand[i]) > lead_rank]
                    
                    if winning:
                        # Win cheaply
                        winning.sort(key=lambda i: get_rank_val(hand[i]))
                        chosen_idx = winning[0]
                    else:
                        # Lose cheaply
                        matches.sort(key=lambda i: get_rank_val(hand[i]))
                        chosen_idx = matches[0]
                else:
                    # Trump or discard
                    trumps = [i for i, c in enumerate(hand) if get_suit(c) == self.trump]
                    if trumps:
                        trumps.sort(key=lambda i: get_rank_val(hand[i]))
                        chosen_idx = trumps[0]
                    else:
                        chosen_idx = min(range(len(hand)), key=lambda i: get_rank_val(hand[i]))

            return hand[chosen_idx]

        except Exception as e:
            print(f"Bot Logic Error: {e}")
            return hand[0] if hand else None

# Singleton Game Instance
active_game = SaatAathGame()