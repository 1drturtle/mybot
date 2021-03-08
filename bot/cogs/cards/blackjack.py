import random


SUITS = ('Spades', 'Clubs', 'Diamonds', 'Hearts')
FACES = ('Jack', 'Queen', 'King')


class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for s in SUITS:
            # 1 - 10
            for v in range(2, 11):
                self.cards.append(Card(s, v))
            # face cards
            for k in FACES:
                self.cards.append(Card(s, 10, k))
            # ace
            self.cards.append(Card(s, 11, 'Ace'))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    @property
    def card_count(self):
        return len(self.cards)

    def __str__(self):
        return f'Deck ({len(self.cards)} cards)'

    def __repr__(self):
        return f'<Deck cards={self.cards!r}>'

    def __len__(self):
        return len(self.cards)


class Card:
    def __init__(self, suit, val, name=None):
        self.suit = suit
        self.value = val
        self.name = name

    @property
    def is_face(self):
        return self.name in FACES

    @property
    def is_ace(self):
        return self.name == 'Ace'

    def __str__(self):
        return f'{self.name if self.name else self.value} of {self.suit}'

    def __repr__(self):
        return f'<Card suit={self.suit}, value={self.value}, name={self.name}>'

