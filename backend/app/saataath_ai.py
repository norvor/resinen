import random

# --- GAME CONFIG ---
# 30 Card Deck: 
# Spades/Hearts: 7, 8, 9, 10, J, Q, K, A (8 cards each)
# Clubs/Diamonds: 8, 9, 10, J, Q, K, A (7 cards each)
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
        
        # Initial Deal: 5 cards each
        # Player gets indices 0-5, Bot gets 5-10
        self.hands[0] = sorted(self.deck[:5], key=lambda c: (c[1], -get_rank_val(c)))
        self.hands[1] = self.deck[5:10]

    def set_trump(self, suit):
        self.trump = suit
        
        # Second Deal: 10 cards each
        # Deck indices: 10-20 (Player), 20-30 (Bot)
        # Total deck size is exactly 30, so this uses all cards.
        self.hands[0].extend(self.deck[10:20])
        self.hands[1].extend(self.deck[20:30])
        
        self.sort_hand(0)
        self.sort_hand(1)
        self.phase = "PLAYING"

    def sort_hand(self, p_idx):
        # Sorts hand: Trump suit first, then others, all by rank
        def sort_key(c):
            s_order = {'S':1, 'H':2, 'C':3, 'D':4}
            # Give Trump suit priority 0 so it floats to top
            s_val = 0 if c[1] == self.trump else s_order.get(c[1], 9)
            return (s_val, -get_rank_val(c))
        
        self.hands[p_idx].sort(key=sort_key)

    def play_card(self, p_idx, card_idx):
        if self.phase == "FINISHED": return False, "Game Over"
        
        hand = self.hands[p_idx]
        if card_idx < 0 or card_idx >= len(hand): 
            return False, "Invalid Card Index"
        
        card = hand[card_idx]
        
        # --- RULE CHECK: MUST FOLLOW SUIT ---
        if len(self.current_trick) > 0:
            lead_card = self.current_trick[0][1]
            lead_suit = get_suit(lead_card)
            played_suit = get_suit(card)
            
            # Check if player actually has the lead suit
            has_suit = any(get_suit(c) == lead_suit for c in hand)
            
            if has_suit and played_suit != lead_suit:
                return False, f"You must play {lead_suit}"

        # Execute Play
        hand.pop(card_idx)
        self.current_trick.append((p_idx, card))
        
        # Check Trick End
        if len(self.current_trick) == 2:
            self.resolve_trick()
        else:
            self.turn = 1 - self.turn # Toggle turn
            
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
        
        # Check Win Condition (Hand is empty)
        if len(self.hands[0]) == 0:
            self.phase = "FINISHED"

    def determine_winner(self, move1, move2):
        # move = (player_idx, card_string)
        p1, card1 = move1
        p2, card2 = move2
        
        s1, s2 = get_suit(card1), get_suit(card2)
        r1, r2 = get_rank_val(card1), get_rank_val(card2)
        
        # 1. Trump wins against non-trump
        if s2 == self.trump and s1 != self.trump: return p2
        if s1 == self.trump and s2 != self.trump: return p1
        
        # 2. Same suit: Higher rank wins
        if s1 == s2:
            return p1 if r1 > r2 else p2
            
        # 3. Different suits (non-trump): Lead card wins
        return p1

    def get_bot_move_idx(self):
        """
        Robust Bot Logic.
        Returns the INDEX of the card in the bot's hand to play.
        """
        try:
            hand = self.hands[1]
            if not hand: return 0 # Should not happen, but prevents crash
            
            # CASE A: Bot is Leading (New Trick)
            if len(self.current_trick) == 0:
                # Strategy: Play highest rank card to force opponents
                return max(range(len(hand)), key=lambda i: get_rank_val(hand[i]))
            
            # CASE B: Bot is Following
            else:
                lead_card = self.current_trick[0][1]
                lead_suit = get_suit(lead_card)
                
                # Find all cards that follow suit
                matches = [i for i, c in enumerate(hand) if get_suit(c) == lead_suit]
                
                if matches:
                    # Can we win this trick?
                    lead_rank = get_rank_val(lead_card)
                    winning_moves = [i for i in matches if get_rank_val(hand[i]) > lead_rank]
                    
                    if winning_moves:
                        # Win cheaply: play the lowest winning card
                        # (Sort by rank ascending, pick first)
                        winning_moves.sort(key=lambda i: get_rank_val(hand[i]))
                        return winning_moves[0]
                    else:
                        # Can't win, throw lowest matching card (save high ones)
                        matches.sort(key=lambda i: get_rank_val(hand[i]))
                        return matches[0]
                
                else:
                    # Cannot follow suit.
                    # Do we have trumps?
                    trumps = [i for i, c in enumerate(hand) if get_suit(c) == self.trump]
                    
                    if trumps:
                        # Play lowest trump to win
                        trumps.sort(key=lambda i: get_rank_val(hand[i]))
                        return trumps[0]
                    else:
                        # No trump, no match. Throw garbage (lowest rank card in hand)
                        return min(range(len(hand)), key=lambda i: get_rank_val(hand[i]))

        except Exception as e:
            print(f"Bot Logic Error: {e}")
            return 0 # Fail-safe: play first card

# Create the single active session
active_game = SaatAathGame()