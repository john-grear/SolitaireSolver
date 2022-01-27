from PyQt5 import QtGui
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from SolitaireSolver import *


# Replaces the current QLabel on the GUI, links information
# to the new QLabel, and creates custom events
class CardImage(QLabel):
    def __init__(self, card, parent, widget, replace=True):
        super().__init__(parent)
        print(SolitaireSolver.s_deck.extra)

        # True = Back showing; False = Face showing
        self.is_flipped = True
        self.is_moving = False
        self.card = card
        self.cards_below = []

        self.setSizePolicy(widget.sizePolicy())
        self.setScaledContents(True)
        self.setMinimumSize(widget.minimumSize())
        self.setPixmap(widget.pixmap())
        self.setGeometry(widget.geometry())
        self.position = (self.geometry().x(), self.geometry().y())

        # Deletes the base widget from the GUI
        if replace:
            widget.setParent(None)

    # Changes image of card to front/back respectively
    # Cards with the back facing cannot be moved
    def flip(self):
        if self.is_flipped:
            self.setPixmap(QPixmap(self.card.image_location()))
        else:
            path = os.getcwd() + "\\resources\\card_back.png"
            self.setPixmap(QPixmap(path))
        self.is_flipped = not self.is_flipped

    # Covered by another card; cannot be moved
    def is_covered(self):
        for card in self.parent().findChildren(QLabel):
            # In same pile and on top of pile
            if abs(self.x() - card.x()) == 0 and card.y() > self.y():
                if card.is_flipped or card.x() < 120:
                    return True
        return False

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if not self.is_flipped and not self.is_covered():
            # Prepares card for moving
            self.is_moving = True
            self.raise_()

            # Prepares the cards below the card for moving
            for card in self.parent().findChildren(QLabel):
                if abs(self.x() - card.x()) == 0 and card.y() > self.y():
                    self.cards_below.append(card)
                    card.raise_()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.is_moving:
            # Moves the center of the top of card to the mouse
            self.move(self.mapToParent(ev.pos().__add__(QPoint(-50, -20))))

            # Moves the cards below the card
            times_to_add = 0
            for card in self.cards_below:
                card.move(self.mapToParent(ev.pos().__add__(QPoint(-50, 20 * times_to_add))))
                times_to_add += 1

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.is_moving = False
        prev_location = (self.position[0], self.position[1])

        # Searches for the closest card in the nearest pile
        closest_card = None
        for card in self.parent().findChildren(QLabel):
            if 39 > abs(card.x() - self.x()) > 0:
                if card.card.is_red() == self.card.is_red():
                    continue
                if card.card.face.value - self.card.face.value != 1:
                    continue
                if card.x() < 120:
                    continue
                if card.is_flipped:
                    continue
                closest_card = card

        # If there is a card to move to
        moved = False
        if closest_card is not None:
            # Moves the card to its new location
            self.move(closest_card.x(), closest_card.y() + 20)
            self.position = (closest_card.x(), closest_card.y() + 20)

            # Moves all the cards below to their new location
            times_to_add = 1
            for card in self.cards_below:
                times_to_add += 1
                prev_pos = closest_card.pos().__add__(QPoint(0, 20 * times_to_add))
                card.move(prev_pos)
                card.position = (prev_pos.x(), prev_pos.y())

            self.cards_below.clear()
            moved = True

        # Handles King's being dropped in empty spaces
        if self.card.face == Face.KING:
            for x_coord in [140, 260, 380, 500, 620, 740, 860]:
                if abs(self.x() - x_coord) <= 20:
                    card_in_spot = False
                    for card in self.parent().findChildren(QLabel):
                        if card.x() == x_coord and card.y() == 20:
                            card_in_spot = True

                    if not card_in_spot and self.position[0] != x_coord:
                        self.move(x_coord, 20)
                        self.position = (self.x(), self.y())

                        # Moves all the cards below to their new location
                        times_to_add = 0
                        for card in self.cards_below:
                            times_to_add += 1
                            prev_pos = self.pos().__add__(QPoint(0, 20 * times_to_add))
                            card.move(prev_pos)
                            card.position = (prev_pos.x(), prev_pos.y())

                        moved = True

        # Moves all cards back if no available spot
        if not moved:
            self.move(self.position[0], self.position[1])
            for card in self.cards_below:
                card.move(card.position[0], card.position[1])
            self.cards_below.clear()
            return

        # Flips next card
        extra_card_pulled = False
        for card in self.parent().findChildren(QLabel):
            if prev_location[0] == card.x():
                if prev_location[1] - 20 == card.y() and card.is_flipped:
                    card.flip()
                    return
                elif card.x() < 120:
                    # Handles Extra Card Pull
                    card.move(card.pos().__add__(QPoint(0, 20)))
                    card.position = (card.x(), card.y())
                    if not extra_card_pulled:
                        new_card = CardImage(SolitaireSolver.s_deck.current_extra(),
                                             self.parent().findChild(QWidget, 'cards'), card, False)
                        new_card.move(card.pos().__add__(QPoint(0, -40)))
                        new_card.position = (new_card.x(), new_card.y())
                        print(SolitaireSolver.s_deck.extra)
                        print(self.card)

                        if SolitaireSolver.s_deck.extra.__contains__(self.card):
                            SolitaireSolver.s_deck.extra.remove(self.card)
                        extra_card_pulled = True

                        # Needs some way to get a QWidget that it can copy and delete
                        # Try to copy QWidget below where this one is supposed to go, then edit it

                        # Delete the card that was pulled from s_deck
                    continue
