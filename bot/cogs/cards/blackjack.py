import random
import discord
import typing


__all__ = ('Deck', 'Card', 'Player', 'Dealer')

SUITS = ('Spades', 'Clubs', 'Diamonds', 'Hearts')
FACES = ('Jack', 'Queen', 'King')


class Deck:
    def __init__(self, shuffle=True):
        self.cards = []
        self.build()
        if shuffle:
            self.shuffle()

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


class Player:
    def __init__(self, player: discord.Member, cards: typing.List[Card] = None,
                 bet: int = 0):
        if cards is None:
            cards = []
        self.cards = cards
        self.player = player
        self.bet = bet

    @property
    def has_face(self):
        return any([c.is_face for c in self.cards])

    @property
    def has_ace(self):
        return any([c.is_ace for c in self.cards])

    @property
    def blackjack(self):
        return self.has_ace and self.has_face

    @property
    def total_value(self):
        return sum([c.value for c in self.cards])

    @property
    def busted(self):
        return self.total_value > 21

    def __str__(self):
        return f'{self.player.display_name}: `[{", ".join(str(card) for card in self.cards)}]` ' \
               f'(Total: `{self.total_value}`)'


class Dealer(Player):
    def __init__(self, cards: typing.List[Card] = None):
        super(Dealer, self).__init__(None, cards, -1)

    def __str__(self):
        return f'Dealer: [`{", ".join(str(card) for card in self.cards)}`] (' \
               f'Total: `{self.total_value}`)'
