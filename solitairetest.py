import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

# Card class representing each playing card
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.is_face_up = False

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def flip(self):
        self.is_face_up = not self.is_face_up

# Deck class to manage the deck of cards
class Deck:
    suits = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self):
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop() if self.cards else None

# Solitaire class to manage the game logic
class Solitaire:
    def __init__(self):
        self.deck = Deck()
        self.tableau = [[] for _ in range(7)]  # 7 tableau piles
        self.foundation = [[] for _ in range(4)]  # 4 foundation piles
        self.stockpile = []
        self.waste_pile = []

        # Deal initial cards to tableau piles
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.deal_card()
                if card:
                    self.tableau[j].append(card)
                    if j == i:  # Flip the top card of each pile
                        card.flip()

# Custom widget for displaying a card
class CardWidget(Widget):
    def __init__(self, card, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.size = (100, 150)

        # Create the label but do not add it yet
        self.label = Label(text=str(self.card), size_hint=(None, None), size=self.size)

        # Draw the card
        self.draw_card()

    def draw_card(self):
        self.canvas.clear()
        with self.canvas:
            if self.card.is_face_up:
                Color(1, 1, 1, 1)  # White background for face-up cards
                Rectangle(pos=self.pos, size=self.size)
                self.label.opacity = 1  # Show label for face-up cards
            else:
                Color(0, 0, 1, 1)  # Blue for face-down cards
                Rectangle(pos=self.pos, size=self.size)
                self.label.opacity = 0  # Hide label for face-down cards

        # Add the label to the widget after drawing the card
        self.add_widget(self.label)

    def on_size(self, *args):
        # Ensure the label is centered within the widget
        self.label.center = self.center

# Main game widget
class SolitaireWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Solitaire()
        self.setup_tableau()

    def setup_tableau(self):
        for i, pile in enumerate(self.game.tableau):
            for j, card in enumerate(pile):
                x = 100 + i * 110
                y = 200 - j * 20  # Stack cards vertically
                card_widget = CardWidget(card)
                card_widget.pos = (x, y)
                self.add_widget(card_widget)

# Kivy app class
class SolitaireApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        game_widget = SolitaireWidget()
        layout.add_widget(game_widget)
        return layout

# Main execution
if __name__ == "__main__":
    SolitaireApp().run()
