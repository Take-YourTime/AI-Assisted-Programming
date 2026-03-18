# https://chatgpt.com/share/671f52bd-99dc-800a-ac70-be394d8703a1



# When start this program, it will display 5 cards and ask you to discard some of them.

# You can enter the indices of the cards you want to discard (e.g., 1,2,4) or type 'none' to keep all cards.

# After discarding, the program will evaluate the final hand and display the result.

# The game will then start a new round with a new set of cards.

# If you want to end the program, just input EOF.

# Author: B113040045許育菖

import random
from PIL import Image, ImageDraw, ImageFont

# Unicode symbols for suits
suits = {
    "hearts": "\u2665",    # ♥
    "diamonds": "\u2666",  # ♦
    "clubs": "\u2663",     # ♣
    "spades": "\u2660"     # ♠
}

# Possible card values
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Function to generate a deck of unique cards
def generate_deck():
    return [(value, suit) for value in values for suit in suits.keys()]

# Function to draw a hand of unique cards
def draw_hand(deck, num_cards=5):
    return random.sample(deck, num_cards)

# Function to display cards
def display_cards(cards):
    width, height = 600, 300  # Increased height
    image = Image.new("RGB", (width, height), "black")  # Black background
    draw = ImageDraw.Draw(image)

    # Define font
    try:
        font = ImageFont.truetype("arial.ttf", 36)  # You can change the font if needed
    except IOError:
        font = ImageFont.load_default()

    # Card dimensions and margin
    card_width, card_height = 80, 120
    card_margin = 10

    for i, (value, suit) in enumerate(cards):
        # Calculate the position of each card
        x = i * (card_width + card_margin) + 20
        y = height // 4

        # Draw the white card background
        draw.rectangle([x, y, x + card_width, y + card_height], fill="white", outline="black")

        # Set text color based on suit
        color = "red" if suit in ["hearts", "diamonds"] else "black"

        # Draw card value in the top-left corner
        value_text = value
        draw.text((x + 5, y + 5), value_text, fill=color, font=font)

        # Draw suit symbol in the top-right corner
        suit_symbol = suits[suit]
        suit_text_x = x + card_width - 25
        draw.text((suit_text_x, y + 5), suit_symbol, fill=color, font=font)

    # Display the image
    image.show()

# Function to evaluate poker hand
def evaluate_hand(cards):
    # Mapping value strings to ranks
    rank_dict = {str(i): i for i in range(2, 11)}
    rank_dict.update({"A": 1, "J": 11, "Q": 12, "K": 13})
    ranks = sorted([rank_dict[card[0]] for card in cards])
    suits_list = [card[1] for card in cards]
    
    # Check for flush
    is_flush = len(set(suits_list)) == 1
    # Check for straight
    is_straight = ranks == list(range(ranks[0], ranks[0] + 5))
    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}

    # Determine hand type
    if is_straight and is_flush:
        return "Straight flush"
    elif 4 in rank_counts.values():
        return "Four of a kind"
    elif sorted(rank_counts.values()) == [2, 3]:
        return "Full house"
    elif 3 in rank_counts.values():
        return "Three of a kind"
    elif is_straight:
        return "Straight"
    elif is_flush:
        return "Flush"
    elif list(rank_counts.values()).count(2) == 2:
        return "Two pair"
    elif 2 in rank_counts.values():
        return "Two of a kind"
    else:
        return "Nothing"

# Main game loop
while True:
    # Generate a deck and draw the initial hand
    deck = generate_deck()
    hand = draw_hand(deck)
    display_cards(hand)

    while True:
        # Ask player for cards to discard
        discard_input = input("What do you want to discard? (Enter numbers, e.g., 1,2,4 or 'none'): ").strip().lower()
        
        if discard_input == "none":
            break
        else:
            try:
                discard_indices = [int(idx) - 1 for idx in discard_input.split(",") if idx.strip().isdigit()]
                discard_indices = [idx for idx in discard_indices if 0 <= idx < 5]
                if not discard_indices:
                    print("Invalid input. Please enter valid card indices.")
                    continue
                
                # Remove selected cards and draw new ones
                for idx in discard_indices:
                    hand[idx] = random.choice([card for card in deck if card not in hand])
                display_cards(hand)
            except ValueError:
                print("Invalid input. Please enter valid card indices.")
                continue

    # Evaluate hand and print result
    result = evaluate_hand(hand)
    print(f"Result: {result}")

    # Draw a new hand for the next round
    print("\n--- Starting New Game ---\n")
