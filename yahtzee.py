import random
from typing import List, Union


class InvalidAction(Exception):
    pass


class Round:
    def __init__(self) -> None:
        self.dice = [
            None,
            None,
            None,
            None,
            None,
        ]
        self.rolls = 0
        self.roll()

    def roll(
        self,
        keep1: bool = False,
        keep2: bool = False,
        keep3: bool = False,
        keep4: bool = False,
        keep5: bool = False,
    ) -> List[int]:
        if self.rolls >= 3:
            raise InvalidAction(f"Already rolled {self.rolls} times")

        self.rolls += 1

        if not keep1:
            self.dice[0] = random.randint(1, 6)
        if not keep2:
            self.dice[1] = random.randint(1, 6)
        if not keep3:
            self.dice[2] = random.randint(1, 6)
        if not keep4:
            self.dice[3] = random.randint(1, 6)
        if not keep5:
            self.dice[4] = random.randint(1, 6)

        return self.dice


class Player:
    def __init__(self) -> None:
        self.scores: List[List[int]] = [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.bonus_yahtzees = 0
        self.rounds = 0

    def open_slots(self) -> List[int]:
        return [i for i in range(0, 12) if self.scores[i] == None]

    def record_round(self, round: Round, index: int) -> bool:
        if index < 0 or index > 13:
            raise InvalidAction(f"Invalid round index {index}")

        if self.scores[index] is not None:
            raise InvalidAction(f"Already scored index {index}")

        if (
            self.scores[11]
            and is_of_kind(self.scores[11], 5)
            and is_of_kind(round.dice, 5)
        ):
            self.bonus_yahtzees += 1

        self.scores[index] = round.dice

        self.rounds += 1
        if self.rounds >= 13:
            return True
        return False

    def current_scores(self) -> List[Union[int, None]]:
        return [
            tally_numbers(self.scores[0], 1, None),
            tally_numbers(self.scores[1], 2, None),
            tally_numbers(self.scores[2], 3, None),
            tally_numbers(self.scores[3], 4, None),
            tally_numbers(self.scores[4], 5, None),
            tally_numbers(self.scores[5], 6, None),
            None
            if self.scores[6] is None
            else (sum(self.scores[6]) if is_of_kind(self.scores[6], 3) else 0),
            None
            if self.scores[7] is None
            else (sum(self.scores[7]) if is_of_kind(self.scores[7], 4) else 0),
            None
            if self.scores[8] is None
            else (25 if is_full_house(self.scores[8]) else 0),
            None
            if self.scores[9] is None
            else (30 if is_small_straight(self.scores[9]) else 0),
            None
            if self.scores[10] is None
            else (40 if is_large_straight(self.scores[10]) else 0),
            None
            if self.scores[11] is None
            else (50 if is_of_kind(self.scores[11], 5) else 0),
            None if self.scores[12] is None else sum(self.scores[12]),
        ]

    def total_score(self) -> int:
        above = (
            tally_numbers(self.scores[0], 1)
            + tally_numbers(self.scores[1], 2)
            + tally_numbers(self.scores[2], 3)
            + tally_numbers(self.scores[3], 4)
            + tally_numbers(self.scores[4], 5)
            + tally_numbers(self.scores[5], 6)
        )
        below = (
            (sum(self.scores[6]) if is_of_kind(self.scores[6], 3) else 0)
            + (sum(self.scores[7]) if is_of_kind(self.scores[7], 4) else 0)
            + (25 if is_full_house(self.scores[8]) else 0)
            + (30 if is_small_straight(self.scores[9]) else 0)
            + (40 if is_large_straight(self.scores[10]) else 0)
            + (50 if is_of_kind(self.scores[11], 5) else 0)
            + (sum(self.scores[12]) if self.scores[12] else 0)
            + (100 * self.bonus_yahtzees)
        )

        return above + (35 if above >= 63 else 0) + below


def tally_numbers(
    dice: Union[List[int], None], number: int, empty_value: Union[int, None] = 0
) -> Union[int, None]:
    if dice is None:
        return empty_value
    matching = [i for i in dice if i == number]
    return len(matching) * number


def number_counts(dice: List[int]) -> List[int]:
    counts = [0, 0, 0, 0, 0, 0]
    for i in dice:
        counts[i - 1] += 1
    return counts


def is_of_kind(dice: List[int], required_count: int) -> bool:
    if dice is None:
        return False
    counts = sorted(number_counts(dice), reverse=True)
    return counts[0] >= required_count


def is_full_house(dice: List[int]) -> bool:
    if dice is None:
        return False
    counts = sorted(number_counts(dice), reverse=True)
    return counts[0] == 5 or (counts[0] == 3 and counts[1] == 2)


def is_small_straight(dice: List[int]) -> bool:
    if dice is None:
        return False
    counts = number_counts(dice)
    return (
        counts[2] > 0
        and counts[3] > 0
        and (
            (counts[1] > 0 and (counts[0] > 0 or counts[4] > 0))
            or (counts[2] > 0 and counts[5] > 0)
        )
    )


def is_large_straight(dice: List[int]) -> bool:
    if dice is None:
        return False
    counts = number_counts(dice)
    return (
        counts[1] > 0
        and counts[2] > 0
        and counts[3] > 0
        and counts[4] > 0
        and (counts[0] > 0 or counts[5] > 0)
    )
