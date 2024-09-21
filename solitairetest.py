import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup

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
        self.foundation = [[] for _ in range(4)]
        self.deal_initial_tableau()
        self.selected_card_widget = None

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
        self.bind(on_touch_down=self.on_card_click)

    def on_card_click(self, widget, touch):
        if self.collide_point(touch.x, touch.y):
            if self.is_selected:
                self.is_selected = False
                self.game.selected_card_widget = None
                self.update_position()
            else:
                if self.game.selected_card_widget:
                    target_card_widget = self
                    if self.can_place_on(target_card_widget.card):
                        source_index = self.game.selected_card_widget.tableau_index
                        self.game.tableau[source_index].remove(self.game.selected_card_widget.card)
                        self.game.tableau[self.tableau_index].append(self.game.selected_card_widget.card)
                        self.update_tableau()
                        target_card_widget.update_tableau()

                        self.game.selected_card_widget.is_selected = False
                        self.game.selected_card_widget.update_position()
                        self.game.selected_card_widget = None

                        if self.game.check_win():
                            self.show_win_popup()
                else:
                    self.is_selected = True
                    self.game.selected_card_widget = self

            self.update_position()
            return True
        return False

    def can_place_on(self, target_card):
        if not target_card.is_face_up:
            return False
        return ((self.card.is_red() and target_card.is_black()) or
                (self.card.is_black() and target_card.is_red())) and \
            (self.rank_value(self.card.rank) == self.rank_value(target_card.rank) - 1)

    def rank_value(self, rank):
        if rank == 'A':
            return 1
        elif rank == 'J':
            return 11
        elif rank == 'Q':
            return 12
        elif rank == 'K':
            return 13
        return int(rank)

    def update_tableau(self):
        if self.game.tableau[self.tableau_index]:
            last_card = self.game.tableau[self.tableau_index][-1]
            if not last_card.is_face_up:
                last_card.flip()

    def show_win_popup(self):
        popup = Popup(title='Congratulations!', content=Label(text='You won the game!'), size_hint=(0.6, 0.6))
        popup.open()

    def update_position(self, *args):
        if self.game.tableau[self.tableau_index]:
            y_offset = 0
            for card in self.game.tableau[self.tableau_index]:
                if card == self.card:
                    self.pos = (self.x, self.game.height - (y_offset * self.height * 0.25 + self.height))
                    break
                y_offset += 1

        self.clear_widgets()
        self.canvas.clear()
        self.draw_card()

    def draw_card(self):
        with self.canvas:
            if self.is_selected:
                Color(1, 1, 0, 1)  # Highlight color (yellow)
                Rectangle(pos=(self.x - 5, self.y - 5), size=(self.width + 10, self.height + 10))

            if self.card.is_face_up:
                Color(1, 1, 1, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0, 0, 0, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

                rank_suit = f"{self.card.rank}{self.card.suit}"
                label = Label(text=rank_suit, color=(1, 0, 0, 1) if self.card.is_red() else (0, 0, 0, 1))
                label.pos = (self.x + 10, self.y + 10)
                label.font_size = self.height * 0.2
                self.add_widget(label)
            else:
                Color(0, 0, 1, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0, 0, 0, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

class SolitaireWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Solitaire()
        self.drawn_card_widget = None
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
            y_offset = 0
            for j, card in enumerate(pile):
                x = pile_width * (i + 1)
                y = self.height - (y_offset * card_height_offset + card_height)

                card_widget = CardWidget(card, i, self.game)
                card_widget.pos = (x, y)
                card_widget.size = (card_width, card_height)
                self.add_widget(card_widget)

                y_offset += 1

        if self.drawn_card_widget:
            self.add_widget(self.drawn_card_widget)

    def draw_card(self):
        if self.game.deck.cards:
            card = self.game.deck.deal_card()
            card.flip()
            card_widget = CardWidget(card, -1, self.game)  # -1 as it doesn't belong to a tableau
            card_widget.size = (100, 150)  # Set size for drawn card
            card_widget.pos = (self.width - 120, self.height - 200)  # Position for drawn card
            self.drawn_card_widget = card_widget
            self.add_widget(card_widget)

    def reset_game(self):
        self.game = Solitaire()
        self.setup_tableau()

class SolitaireApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        Window.size = (1080, 1980)
        game_widget = SolitaireWidget()

        draw_button = Button(text='Draw Card', size_hint=(0.1, 0.1))
        draw_button.bind(on_release=lambda instance: game_widget.draw_card())

        reset_button = Button(text='Reset Game', size_hint=(0.1, 0.1))
        reset_button.bind(on_release=game_widget.reset_game)

        layout.add_widget(game_widget)
        layout.add_widget(draw_button)
        layout.add_widget(reset_button)

        return layout

if __name__ == "__main__":
    SolitaireApp().run()
