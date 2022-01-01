import random
import click
import os.path
from typing import List, Union

import numpy

from agent import RollAgent, SlotAgent
from yahtzee import InvalidAction, Player, Round


@click.command("run")
@click.option("-r", "--roll-weights", "roll_weights_path", type=str)
@click.option("-w", "--slot-weights", "slot_weights_path", type=str)
@click.option("-i", "--iterations", "iterations", type=int, default=50)
@click.option("-t", "--train", "train", type=str, default="all")
@click.option("-s", "--batch-size", "batch_size", type=int, default=1000)
@click.option("-e", "--epsilon", "epsilon", type=float, default=1.0)
def run(
    roll_weights_path: Union[str, None],
    slot_weights_path: Union[str, None],
    iterations: int,
    train: bool,
    batch_size: int,
    epsilon: float,
):
    train_roll = train == "all" or train == "roll"
    train_slot = train == "all" or train == "slot"
    print("Starting...")
    print("Initializing agents...")
    roll_agent = RollAgent(
        weights_path=roll_weights_path,
        input_size=19,
        output_size=32,
        epsilon=1,
    )
    slot_agent = SlotAgent(
        weights_path=slot_weights_path, input_size=18, output_size=13, epsilon=epsilon
    )

    if roll_weights_path and os.path.exists(roll_weights_path):
        print(f"Loading roll weights: {roll_weights_path}")
        roll_agent.model.load_weights(roll_weights_path)

    if slot_weights_path and os.path.exists(slot_weights_path):
        print(f"Loading roll weights: {slot_weights_path}")
        slot_agent.model.load_weights(slot_weights_path)

    games_run = 0

    while games_run < iterations:
        print(f"Running game #{games_run + 1}")
        player = Player()
        current_score = 0
        round_number = 1
        while not len(player.open_slots()) == 0:
            print(f"Round #{round_number}")
            round = Round()
            roll_states = []
            while round.rolls < 1:
                state_old = roll_agent.get_state(player, round)
                roll_prediction = roll_agent.predict(state_old)
                for index in ordered_prediction(roll_prediction):
                    try:
                        keep = [
                            True if char == "1" else False
                            for char in format(int(index), "05b")
                        ]
                        print(f"keeping: {keep}")
                        round.roll(keep[0], keep[1], keep[2], keep[3], keep[4])
                    except InvalidAction:
                        continue

                    break

                if train_roll:
                    state_new = roll_agent.get_state(player, round)
                    roll_states.append(
                        (state_old, int(index), state_new, round.rolls == 3)
                    )

            state_old = slot_agent.get_state(player, round)
            slot_prediction = slot_agent.predict(state_old)
            for index in ordered_prediction(slot_prediction):
                try:
                    player.record_round(round, int(index))
                    print(round.dice)
                    print(f"recorded in slot: {index}")
                except InvalidAction as e:
                    # print(e)
                    continue

                break
            new_score = player.total_score()
            reward = new_score - current_score
            current_score = new_score
            print(f"reward: {reward}")

            if train_slot:
                state_new = slot_agent.get_state(player, round)
                done = len(player.open_slots()) == 0
                slot_agent.train_short_memory(
                    state_old, int(index), reward, state_new, done
                )
                slot_agent.remember(state_old, int(index), reward, state_new, done)

            if train_roll:
                for (state_old, number, state_new, done) in roll_states:
                    roll_agent.train_short_memory(
                        state_old, number, reward, state_new, done
                    )
                    roll_agent.remember(state_old, number, reward, state_new, done)

            round_number += 1

        games_run += 1
        print(f"Game {games_run}\tScore: {player.total_score()}")

        if train_slot:
            print("updating slot models")
            slot_agent.replay_new(slot_agent.memory, batch_size)
            slot_agent.model.save_weights(slot_weights_path)
        
        if train_roll:
            print("updating roll models")
            roll_agent.replay_new(roll_agent.memory, batch_size)
            roll_agent.model.save_weights(roll_weights_path)


def ordered_prediction(probability_vector: numpy.ndarray) -> List[int]:
    full_size = len(probability_vector)
    size = len([p for p in probability_vector if p > 0])
    picks = list(
        numpy.random.choice(
            range(0, full_size), size, p=probability_vector, replace=False
        )
    )

    if size < full_size:
        extra_indexes = [i for i in range(0, full_size) if probability_vector[i] == 0]
        random.shuffle(extra_indexes)
        picks.extend(extra_indexes)

    return picks


if __name__ == "__main__":
    run()
