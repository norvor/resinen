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
def get_rank_val(card): return RANK_MAP.get(card[0], 0) # Safety .get()

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
        # Full Deal
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
        if self.phase == "FINISHED": return False, "Game Over"
        
        hand = self.hands[p_idx]
        if card not in hand: return False, "Card not in hand"
            
        # Rule Check: Must Follow Suit
        if len(self.current_trick) > 0:
            lead_card = self.current_trick[0][1]
            lead_suit = get_suit(lead_card)
            played_suit = get_suit(card)
            
            has_suit = any(get_suit(c) == lead_suit for c in hand)
            if has_suit and played_suit != lead_suit:
                return False, f"Must follow {lead_suit}"

        # Execute
        hand.remove(card)
        self.current_trick.append((p_idx, card))
        
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
        
        self.last_trick = list(self.current_trick)
        self.last_winner = winner
        self.current_trick = [] 
        
        # Check Win Condition
        if len(self.hands[0]) == 0:
            self.phase = "FINISHED"

    def determine_winner(self, move1, move2):
        p1, card1 = move1
        p2, card2 = move2
        
        s1, s2 = get_suit(card1), get_suit(card2)
        r1, r2 = get_rank_val(card1), get_rank_val(card2)
        
        if s2 == self.trump and s1 != self.trump: return p2
        if s1 == self.trump and s2 != self.trump: return p1
        if s1 == s2: return p1 if r1 > r2 else p2
        return p1

    def get_bot_move_card(self):
        """
        CRASH-PROOF BOT LOGIC
        Wraps decision making in a sandbox. 
        If logic fails, it plays the first valid card it finds.
        """
        try:
            hand = self.hands[1]
            if not hand: return None
            
            # --- STRATEGIC BLOCK ---
            chosen_card = None
            
            if len(self.current_trick) == 0:
                # Leading: Play highest rank (Simple Strategy)
                # Sort by rank desc, pick first
                sorted_hand = sorted(hand, key=lambda c: -get_rank_val(c))
                chosen_card = sorted_hand[0]
            else:
                # Following
                lead_card = self.current_trick[0][1]
                lead_suit = get_suit(lead_card)
                matches = [c for c in hand if get_suit(c) == lead_suit]
                
                if matches:
                    # Try to win
                    lead_rank = get_rank_val(lead_card)
                    winning = [c for c in matches if get_rank_val(c) > lead_rank]
                    
                    if winning:
                        # Win cheap: Lowest winning card
                        chosen_card = sorted(winning, key=lambda c: get_rank_val(c))[0]
                    else:
                        # Lose cheap: Lowest matching card
                        chosen_card = sorted(matches, key=lambda c: get_rank_val(c))[0]
                else:
                    # Can't follow suit
                    trumps = [c for c in hand if get_suit(c) == self.trump]
                    if trumps:
                        # Trump cheap: Lowest trump
                        chosen_card = sorted(trumps, key=lambda c: get_rank_val(c))[0]
                    else:
                        # Discard junk: Lowest card overall
                        chosen_card = sorted(hand, key=lambda c: get_rank_val(c))[0]

            # --- VALIDATION BLOCK ---
            # Ensure chosen_card is actually in hand (Sanity Check)
            if chosen_card and chosen_card in hand:
                return chosen_card
                
            # Fallback if logic failed to pick
            return hand[0]

        except Exception as e:
            print(f"CRITICAL BOT ERROR: {e}")
            # ULTIMATE FALLBACK: Play first available card
            # This prevents the server from crashing on logic errors
            if self.hands[1]:
                return self.hands[1][0]
            return None

# Singleton Game Instance
active_game = SaatAathGame()