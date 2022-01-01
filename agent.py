from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
import numpy
import collections
import random
from typing import List, Union

from yahtzee import Player, Round


class State:
    def __init__(self, data: List[int] = []) -> None:
        self.data = data
        self.num_fields = len(data)

    def to_data(self) -> List[int]:
        return numpy.asarray(self.data)


class Agent:
    """Deep Q-Network Agent"""

    def __init__(
        self,
        weights_path: str,
        input_size: int,
        output_size: int,
        learning_rate: float = 0.0005,
        first_layer_size: int = 50,
        second_layer_size: int = 300,
        third_layer_size: int = 50,
        memory_size: int = 2500,
        load_weights: bool = False,
    ) -> None:
        self.gamma = 0.9
        self.short_memory = numpy.array([])
        self.learning_rate = learning_rate
        self.epsilon = 1
        self.first_layer = first_layer_size
        self.second_layer = second_layer_size
        self.third_layer = third_layer_size
        self.input_size = input_size
        self.output_size = output_size
        self.memory = collections.deque(maxlen=memory_size)
        self.weights = weights_path
        self.load_weights = load_weights
        self.model = self.network()

    def network(self):
        model = Sequential()
        model.add(Input(shape=(self.input_size)))
        model.add(Dense(self.first_layer, activation="relu"))
        model.add(Dense(self.second_layer, activation="relu"))
        model.add(Dense(self.third_layer, activation="relu"))
        model.add(Dense(self.output_size, activation="softmax"))
        opt = Adam(self.learning_rate)
        model.compile(loss="mse", optimizer=opt)

        if self.load_weights:
            model.load_weights(self.weights)
        return model

    def get_state(self, player: Player, round: Round) -> State:
        raise Exception("Not implemented")

    def get_reward(self, player: Player, round: Round):
        return player.total_score()

    def remember(
        self, state: State, action: int, reward: int, next_state: State, done: bool
    ):
        self.memory.append(
            (state.to_data(), action, reward, next_state.to_data(), done)
        )

    def replay_new(self, memory, batch_size):
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * numpy.amax(
                    self.model.predict(numpy.array([next_state]))[0]
                )
            target_f = self.model.predict(numpy.array([state]))
            target_f[0][numpy.argmax(action)] = target
            self.model.fit(numpy.array([state]), target_f, epochs=1, verbose=0)

    def train_short_memory(
        self, state: State, action: int, reward: int, next_state: State, done: bool
    ):
        target = reward
        if not done:
            target = reward + self.gamma * numpy.amax(
                self.model.predict(
                    next_state.to_data().reshape((1, next_state.num_fields))
                )[0]
            )
        target_f = self.model.predict(state.to_data().reshape((1, state.num_fields)))
        target_f[0][numpy.argmax(action)] = target
        self.model.fit(
            state.to_data().reshape((1, state.num_fields)),
            target_f,
            epochs=1,
            verbose=0,
        )

    def predict(self, state_old: State) -> List[List[Union[int, float]]]:
        if random.uniform(0, 1) < self.epsilon:
            weights = to_categorical(
                random.randint(0, self.output_size - 1), num_classes=self.output_size
            )
        else:
            # predict action based on the old state
            prediction = self.model.predict(
                state_old.reshape((1, state_old.num_fields))
            )
            weights = to_categorical(
                numpy.argmax(prediction[0]), num_classes=self.output_size
            )

        with_index = numpy.array(list(zip(weights, range(0, weights.size))))
        return with_index[numpy.argsort(with_index[:, 0])]


class RollAgent(Agent):
    def get_state(self, player: Player, round: Round) -> State:
        state = [
            score if score is not None else -1 for score in player.current_scores()
        ]
        state.extend(round.dice)
        state.append(round.rolls)
        return State(state)


class SlotAgent(Agent):
    def get_state(self, player: Player, round: Round) -> State:
        state = [
            score if score is not None else -1 for score in player.current_scores()
        ]
        state.extend(round.dice)
        return State(state)
