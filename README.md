# Yahtzee with Machine Learning

This is an experiment to build a simple game (Yahtzee) and
train an AI Agent using Deep Q-Learning.

## CLI Game

To play an interactive game yourself, run:

```bash
python3 cli.py
```

## Train Agents

The AI model has 2 agents:

1. Deciding which dice to keep/re-roll
2. Deciding where to score the dice

To train the model, run:

```bash
python3 train.py --roll-weights=path/to/roll.hdf5 \
  --slot-weights=path/to/slot.hdf5
```
