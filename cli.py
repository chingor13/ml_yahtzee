import click
from yahtzee import InvalidAction, Player, Round

from typing import List


@click.command()
def run():
    player = Player()
    while player.rounds < 13:
        round = Round()
        while round.rolls < 3:
            print(round.dice)
            while True:
                try:
                    value = click.prompt("Enter dice to keep", default="")
                    keep = parse(value)
                    round.roll(keep[0], keep[1], keep[2], keep[3], keep[4])
                except ValueError:
                    continue
                break
        print(round.dice)
        print_scorecard(player)
        while True:
            try:
                value = click.prompt("Where to score", type=int)
                player.record_round(round, value - 1)
            except InvalidAction:
                continue
            break

        print_scorecard(player)
    print("Total score:")
    print(player.total_score())


def parse(input: str) -> List[bool]:
    options = [False, False, False, False, False]
    for char in input:
        num_value = int(char)
        if num_value >= 1 and num_value <= 5:
            options[num_value - 1] = True
        else:
            raise ValueError(f"Invalid entry {input}")
    return options


def print_scorecard(player: Player) -> None:
    player_scores = player.current_scores()
    print(f"1\t1s\t\t{player_scores[0]}")
    print(f"2\t2s\t\t{player_scores[1]}")
    print(f"3\t3s\t\t{player_scores[2]}")
    print(f"4\t4s\t\t{player_scores[3]}")
    print(f"5\t5s\t\t{player_scores[4]}")
    print(f"6\t6s\t\t{player_scores[5]}")
    print(f"7\t3 of a kind\t{player_scores[6]}")
    print(f"8\t4 of a kind\t{player_scores[7]}")
    print(f"9\tFull House\t{player_scores[8]}")
    print(f"10\tSmall Straight\t{player_scores[9]}")
    print(f"11\tLarge Straight\t{player_scores[10]}")
    print(f"12\tYahtzee\t\t{player_scores[11]}")
    print(f"13\tChance\t\t{player_scores[12]}")
    print(f"\tBonus Yahtzees\t{player.bonus_yahtzees}")


if __name__ == "__main__":
    run()
