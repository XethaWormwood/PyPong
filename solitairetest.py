import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.is_face_up = False

    def flip(self):
        self.is_face_up = not self.is_face_up

    def is_red(self):
        return self.suit in ['H', 'D']

class Deck:
    suits = ['H', 'D', 'C', 'S']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    def __init__(self):
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop() if self.cards else None

class Solitaire:
    def __init__(self):
        self.deck = Deck()
        self.tableau = [[] for _ in range(7)]
        self.deal_initial_tableau()

    def deal_initial_tableau(self):
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.deal_card()
                if card:
                    self.tableau[j].append(card)
                    if j == i:
                        card.flip()

class CardWidget(Widget):
    def __init__(self, card, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.size_hint = (None, None)
        self.bind(pos=self.update_position, size=self.update_position)
        self.draw_card()

    def update_position(self, *args):
        self.clear_widgets()
        self.canvas.clear()
        self.draw_card()

    def draw_card(self):
        with self.canvas:
            if self.card.is_face_up:
                Color(1, 1, 1, 1)  # White for face-up cards
                Rectangle(pos=self.pos, size=self.size)
                Color(0, 0, 0, 1)  # Black border
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

                # Display rank and suit
                rank_suit = f"{self.card.rank}{self.card.suit}"
                self.label = Label(text=rank_suit, color=(1, 0, 0, 1) if self.card.is_red() else (0, 0, 0, 1))
                self.label.pos = (self.x + 10, self.y + 10)
                self.label.font_size = self.height * 0.2
                self.add_widget(self.label)
            else:
                Color(0, 0, 1, 1)  # Blue for face-down cards
                Rectangle(pos=self.pos, size=self.size)
                Color(0, 0, 0, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

class SolitaireWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Solitaire()
        self.bind(size=self.on_size)
        self.setup_tableau()

    def on_size(self, *args):
        self.setup_tableau()

    def setup_tableau(self):
        self.clear_widgets()
        num_piles = 7
        pile_width = self.width / (num_piles + 1)
        card_width = pile_width * 0.8
        card_height = card_width * 1.5
        card_height_offset = card_height * 0.25

        for i, pile in enumerate(self.game.tableau):
            for j, card in enumerate(pile):
                x = pile_width * (i + 1)
                y = self.height - (j * card_height_offset + card_height)

                card_widget = CardWidget(card)
                card_widget.pos = (x, y)
                card_widget.size = (card_width, card_height)
                self.add_widget(card_widget)

class SolitaireApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        Window.size = (800, 600)
        game_widget = SolitaireWidget()
        layout.add_widget(game_widget)
        return layout

if __name__ == "__main__":
    SolitaireApp().run()
