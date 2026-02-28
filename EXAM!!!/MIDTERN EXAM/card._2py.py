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

# Randomly generate 5 cards (suit, value)
cards = [(random.choice(values), random.choice(list(suits.keys()))) for _ in range(5)]

# Create an image with increased height
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
    suit_text_x = x + card_width - 25  # Adjust the horizontal position for the suit symbol
    draw.text((suit_text_x, y + 5), suit_symbol, fill=color, font=font)

# Display the image
image.show()
