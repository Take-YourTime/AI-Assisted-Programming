from PIL import Image, ImageDraw, ImageFont
import random

# Define the ranks and suits for a standard deck of cards
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
suits = ["♠", "♥", "♦", "♣"]
card_width, card_height = 200, 300  # Dimensions of each card
num_cards = 5  # Number of cards to generate

# Initialize list to hold card images
cards = []

# Generate 5 random card images
for _ in range(num_cards):
    # Create a blank white image for each card
    card_img = Image.new("RGB", (card_width, card_height), "white")
    draw = ImageDraw.Draw(card_img)
    
    # Choose a random rank and suit
    rank = random.choice(ranks)
    suit = random.choice(suits)
    
    # Draw a simple border around the card
    draw.rectangle([(5, 5), (card_width-5, card_height-5)], outline="black", width=3)
    
    # Define positions and sizes
    suit_size = 50  # Size of the suit symbol
    text_position = (card_width // 2, card_height // 2)
    corner_position = (20, 20)
    
    # Load a default font
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the rank and suit in the center of the card
    draw.text(text_position, f"{rank}{suit}", font=font, fill="black", anchor="mm")
    
    # Draw the rank and suit in the top-left corner as well
    draw.text(corner_position, f"{rank}\n{suit}", font=font, fill="black")
    
    # Append the card image to our list
    cards.append(card_img)

# Display the generated card images
cards[0].show()  # Displaying only the first card to check the output
cards
