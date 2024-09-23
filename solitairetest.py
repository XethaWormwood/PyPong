import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.label import Label
from kivy.uix.popup import Popup
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

    def is_black(self):
        return self.suit in ['C', 'S']

    def rank_value(self):
        if self.rank == 'A':
            return 1
        elif self.rank == 'J':
            return 11
        elif self.rank == 'Q':
            return 12
        elif self.rank == 'K':
            return 13
        return int(self.rank)

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
        self.waste_pile = []  # Waste pile
        self.tableau = [[] for _ in range(7)]
        self.foundation = [[] for _ in range(4)]
        self.moves = []
        self.score = 0
        self.undo_limit = 3  # Limit the number of undo moves
        self.deal_initial_tableau()

    def deal_initial_tableau(self):
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.deal_card()
                if card:
                    self.tableau[j].append(card)
                    if j == i:
                        card.flip()

    def check_win(self):
        return all(len(foundation) == 13 for foundation in self.foundation)

    def undo_move(self):
        if self.moves and len(self.moves) < self.undo_limit:
            last_move = self.moves.pop()
            source_index, target_index, cards = last_move
            self.tableau[source_index].extend(cards)
            for card in cards:
                self.tableau[target_index].remove(card)
            self.score -= 1

    def can_move_to_foundation(self, card, foundation_pile):
        if not foundation_pile:
            return card.rank == 'A'  # Only Aces can start a foundation pile
        top_card = foundation_pile[-1]
        return card.suit == top_card.suit and card.rank_value() == top_card.rank_value() + 1

    def move_to_foundation(self, card, foundation_index):
        if self.can_move_to_foundation(card, self.foundation[foundation_index]):
            self.foundation[foundation_index].append(card)
            self.score += 10  # Add points for moving to foundation

class CardWidget(Widget):
    def __init__(self, card, tableau_index, game, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.tableau_index = tableau_index
        self.game = game
        self.size_hint = (None, None)
        self.is_selected = False
        self.bind(pos=self.update_position, size=self.update_position)
        self.draw_card()

        self.dragging = False
        self.original_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.card.is_face_up:
                self.dragging = True
                self.original_pos = self.pos
                self.is_selected = True  # Mark this card as selected
                return True
            else:
                self.card.flip()  # Flip the card if it's face down
                self.update_position()
            return True
        return False

    def on_touch_move(self, touch):
        if self.dragging:
            self.pos = (touch.x - self.width / 2, touch.y - self.height / 2)
            return True
        return False

    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            if self.is_valid_drop():
                self.snap_to_new_position()
            else:
                # Return card to its original position if drop is invalid
                self.pos = self.original_pos
            self.is_selected = False  # Reset selection state
            return True
        return False

    def is_valid_drop(self):
        """Check if the card can be dropped on a valid tableau stack."""
        for pile_index, pile in enumerate(self.game.tableau):
            if pile and pile[-1].is_face_up:
                top_card = pile[-1]
                if self.can_place_on(top_card):
                    self.tableau_index = pile_index
                    return True
            elif not pile and self.card.rank == 'K':  # Only kings can start an empty tableau
                self.tableau_index = pile_index
                return True
        return False

    def can_place_on(self, target_card):
        """Check if the current card can be placed on the target card."""
        return ((self.card.is_red() and target_card.is_black()) or
                (self.card.is_black() and target_card.is_red())) and \
            (self.card.rank_value() == target_card.rank_value() - 1)

    def snap_to_new_position(self):
        """Snap the card to its new tableau stack."""
        self.game.tableau[self.tableau_index].append(self.card)
        self.game.score += 1
        self.update_position()  # Update position after moving
        if self.game.check_win():
            self.show_win_popup()

    def update_position(self, *args):
        if self.tableau_index is not None and self.parent:
            y_offset = 0
            for card in self.game.tableau[self.tableau_index]:
                if card == self.card:
                    self.pos = (self.x, self.parent.height - (y_offset * self.height * 0.25 + self.height))
                    break
                y_offset += 1
        else:
            self.pos = self.pos

        self.clear_widgets()
        self.canvas.clear()
        self.draw_card()

    def draw_card(self):
        with self.canvas:
            if self.card.is_face_up:
                Color(1, 1, 1, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0, 0, 0, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

                rank_suit = f"{self.card.rank}{self.card.suit}"
                label = Label(text=rank_suit, color=(1, 0, 0, 1) if self.card.is_red() else (0, 0, 0, 1))
                label.pos = (self.x - 30, self.y + self.height - 65)  # Move label higher
                label.font_size = self.height * 0.15
                self.add_widget(label)
            else:
                Color(0, 0, 0.5, 1)  # Lighter blue for face-down cards
                Rectangle(pos=self.pos, size=self.size)
                Color(0, 0, 0, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

    def show_win_popup(self):
        popup = Popup(title='Congratulations!', content=Label(text='You won the game!'), size_hint=(0.6, 0.6))
        popup.open()

class SolitaireWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Solitaire()
        self.bind(size=self.on_size)

        # Initialize score label
        self.score_label = Label(text=f'Score: {self.game.score}', size_hint=(None, None), size=(200, 50))
        self.score_label.pos = (10, self.height - 50)
        self.add_widget(self.score_label)

        self.setup_tableau()

    def on_size(self, *args):
        self.setup_tableau()
        self.score_label.pos = (10, self.height - 50)

    def setup_tableau(self):
        self.clear_widgets()
        num_piles = 7
        pile_width = self.width / (num_piles + 1)
        card_width = pile_width * 0.8
        card_height = card_width * 1.5
        card_height_offset = card_height * 0.25

        for i, pile in enumerate(self.game.tableau):
            x = (i + 1) * pile_width - card_width / 2
            for j, card in enumerate(pile):
                y = self.height - (j + 1) * card_height_offset - card_height
                card_widget = CardWidget(card, i, self.game, size=(card_width, card_height))
                card_widget.pos = (x, y)
                self.add_widget(card_widget)

        # Redraw the score label after adding all cards
        self.add_widget(self.score_label)
        self.score_label.text = f'Score: {self.game.score}'

class SolitaireApp(App):
    def build(self):
        Window.clearcolor = (0, 0.5, 0.2, 1)
        return SolitaireWidget()

if __name__ == '__main__':
    SolitaireApp().run()
