# from typing import List
import gym
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gym import spaces
from gym.utils import seeding
from stable_baselines3.common.vec_env import DummyVecEnv

matplotlib.use('Agg')

# from stable_baselines3.common.logger import Logger, KVWriter, CSVOutputFormat


class StockTradingEnv(gym.Env):
    """A stock trading environment for OpenAI gym"""

    metadata = {'render.modes': ['human']}

    def __init__(
        self,
        df,
        stock_dim,
        hmax,
        initial_amount,
        num_stock_shares,
        buy_cost_pct,
        sell_cost_pct,
        reward_scaling,
        state_space,
        action_space,
        tech_indicator_list,
        turbulence_threshold=None,
        risk_indicator_col='turbulence',
        make_plots: bool = False,
        print_verbosity=10,
        day=0,
        initial=True,
        previous_state=[],
        model_name='',
        mode='',
        iteration='',
    ):
        """
        Initializes the results object

        Args:
            df: stock dataframe
            stock_dim: dimensions of stock df
            hmax: max number of stocks to buy or sell each step
            initial_amount: starting $ amount
            num_stock_shares: number of stocks shares to start with
            buy_cost_pct: the costs of buying each stock
            sell_cost_pct: the cost of selling each stock
            reward_scaling: amount to scale the rewards by
            state_space: dimensions of states
            action_space: dimensions of actions
            tech_indicator_list: list of technical indicators
            turbulence_threshold: the threshold of turbulence to liquidate
            risk_indicator_col: the column which indicates risk
            make_plots: create plots when finished [y/n]
            print_verbosity: output verbose [1-10]
            day: day of week as integer
            initial: is this the initial state
            previous_state: information on the previous state
            model_name: name of the model
            mode: type of modelling
            iteration: the number of iterations completed
        """
        self.day = day
        self.df = df
        self.stock_dim = stock_dim
        self.hmax = hmax
        self.num_stock_shares = num_stock_shares
        self.initial_amount = initial_amount  # get the initial cash
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.reward_scaling = reward_scaling
        self.state_space = state_space
        self.action_space = action_space
        self.tech_indicator_list = tech_indicator_list
        self.action_space = spaces.Box(low=-1, high=1, shape=(self.action_space,))
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.state_space,)
        )
        self.data = self.df.loc[self.day, :]
        self.terminal = False
        self.make_plots = make_plots
        self.print_verbosity = print_verbosity
        self.turbulence_threshold = turbulence_threshold
        self.risk_indicator_col = risk_indicator_col
        self.initial = initial
        self.previous_state = previous_state
        self.model_name = model_name
        self.mode = mode
        self.iteration = iteration
        # initalize state
        self.state = self._initiate_state()

        # initialize reward
        self.reward = 0
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0
        # memorize all the total balance change
        self.asset_memory = [
            self.initial_amount + np.sum(
                np.array(self.num_stock_shares) * np.array(
                    self.state[1: 1 + self.stock_dim])
            )
        ]
        # the initial total asset is calculated by cash + sum (num_share_stock_i * price_stock_i)
        self.rewards_memory = []
        self.actions_memory = []
        self.state_memory = (
            []
        )  # we need sometimes to preserve the state in the middle of trading process
        self.date_memory = [self._get_date()]
        # self.logger = Logger('results',[CSVOutputFormat])
        # self.reset()
        self._seed()

    def _sell_stock(self, index, action):
        """
        Perform stock sell actions on the specified index.

        Args:
            index: index of stock
            action: magnitude of sell action
        """
        def _do_sell_normal():
            """
            Do the sell action if the stock is not able to sell in that day.
            """
            if (
                self.state[index + 2 * self.stock_dim + 1] != True
            ):  # check if the stock is able to sell,
                # for simlicity we just add it in techical index
                # if self.state[index + 1] > 0:
                # if we use price<0 to denote a stock is unable to trade in that day
                # , the total asset calculation may be wrong for the price is unreasonable
                # Sell only if the price is > 0 (no missing data in this particular date)
                # perform sell action based on the sign of the action
                if self.state[index + self.stock_dim + 1] > 0:
                    # Sell only if current asset is > 0
                    sell_num_shares = min(
                        abs(action), self.state[index + self.stock_dim + 1]
                    )
                    sell_amount = (
                        self.state[index + 1] * sell_num_shares * (
                            1 - self.sell_cost_pct[index])
                    )
                    # update balance
                    self.state[0] += sell_amount

                    self.state[index + self.stock_dim + 1] -= sell_num_shares
                    self.cost += (
                        self.state[index + 1] * sell_num_shares * self.sell_cost_pct[index]
                    )
                    self.trades += 1
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = 0

            return sell_num_shares

        # perform sell action based on the sign of the action
        if self.turbulence_threshold is not None:
            if self.turbulence >= self.turbulence_threshold:
                if self.state[index + 1] > 0:
                    # Sell only if the price is > 0 (no missing data in this particular date)
                    # if turbulence goes over threshold, just clear out all positions
                    if self.state[index + self.stock_dim + 1] > 0:
                        # Sell only if current asset is > 0
                        sell_num_shares = self.state[index + self.stock_dim + 1]
                        sell_amount = (
                            self.state[index + 1] * sell_num_shares * (
                                1 - self.sell_cost_pct[index])
                        )
                        # update balance
                        self.state[0] += sell_amount
                        self.state[index + self.stock_dim + 1] = 0
                        self.cost += (
                            self.state[index + 1] * sell_num_shares * self.sell_cost_pct[index]
                        )
                        self.trades += 1
                    else:
                        sell_num_shares = 0
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = _do_sell_normal()
        else:
            sell_num_shares = _do_sell_normal()

        return sell_num_shares

    def _buy_stock(self, index, action):
        """
        Performs a buy action on the stock at the given index.

        Args:
            index: index of ticker
            action: magnitude of buy action
        """
        def _do_buy():
            """
            Calculates the amount of shares to buy.
            """
            if (
                self.state[index + 2 * self.stock_dim + 1] != True
            ):  # check if the stock is able to buy
                # if self.state[index + 1] >0:
                # Buy only if the price is > 0 (no missing data in this particular date)
                available_amount = self.state[0] // (
                    self.state[index + 1] * (1 + self.buy_cost_pct[index])
                )  # we should consider the cost of trading when calculating available_amount
                # , or we may be have cash<0
                # print('available_amount:{}'.format(available_amount))

                # update balance
                buy_num_shares = min(available_amount, action)
                buy_amount = (
                    self.state[index + 1] * buy_num_shares * (1 + self.buy_cost_pct[index])
                )
                self.state[0] -= buy_amount

                self.state[index + self.stock_dim + 1] += buy_num_shares

                self.cost += (
                    self.state[index + 1] * buy_num_shares * self.buy_cost_pct[index]
                )
                self.trades += 1
            else:
                buy_num_shares = 0

            return buy_num_shares

        # perform buy action based on the sign of the action
        if self.turbulence_threshold is None:
            buy_num_shares = _do_buy()
        else:
            if self.turbulence < self.turbulence_threshold:
                buy_num_shares = _do_buy()
            else:
                buy_num_shares = 0
        return buy_num_shares

    def _make_plot(self):
        """
        Makes the plot
        """
        plt.plot(self.asset_memory, 'r')
        plt.savefig(f'results/account_value_trade_{self.episode}.png')
        plt.close()

    def step(self, actions):
        """
        Take one step of simulation.

        Args:
            actions: actions to take this step
        """
        self.terminal = self.day >= len(self.df.index.unique()) - 1
        if self.terminal:
            # print(f"Episode: {self.episode}")
            if self.make_plots:
                self._make_plot()
            end_total_asset = self.state[0] + sum(
                np.array(self.state[1: (self.stock_dim + 1)]) * np.array(
                    self.state[(self.stock_dim + 1): (self.stock_dim * 2 + 1)])
            )
            df_total_value = pd.DataFrame(self.asset_memory)
            tot_reward = (
                self.state[0] + sum(
                    np.array(self.state[1: (self.stock_dim + 1)]) * np.array(
                        self.state[(self.stock_dim + 1): (self.stock_dim * 2 + 1)]
                    )
                ) - self.asset_memory[0]
            )  # initial_amount is only cash part of our initial asset
            df_total_value.columns = ['account_value']
            df_total_value['date'] = self.date_memory
            df_total_value['daily_return'] = df_total_value['account_value'].pct_change(
                1
            )
            if df_total_value['daily_return'].std() != 0:
                sharpe = (
                    (252**0.5) * df_total_value['daily_return']
                    .mean() / df_total_value['daily_return'].std()
                )
            df_rewards = pd.DataFrame(self.rewards_memory)
            df_rewards.columns = ['account_rewards']
            df_rewards['date'] = self.date_memory[:-1]
            if self.episode % self.print_verbosity == 0:
                print(f'day: {self.day}, episode: {self.episode}')
                print(f'begin_total_asset: {self.asset_memory[0]:0.2f}')
                print(f'end_total_asset: {end_total_asset:0.2f}')
                print(f'total_reward: {tot_reward:0.2f}')
                print(f'total_cost: {self.cost:0.2f}')
                print(f'total_trades: {self.trades}')
                if df_total_value['daily_return'].std() != 0:
                    print(f'Sharpe: {sharpe:0.3f}')
                print('=================================')

            if (self.model_name != '') and (self.mode != ''):
                df_actions = self.save_action_memory()
                df_actions.to_csv(
                    f'results/actions_{self.mode}_{self.model_name}_{self.iteration}.csv'
                )
                df_total_value.to_csv(
                    f'results/account_value_{self.mode}_{self.model_name}_{self.iteration}.csv',
                    index=False,
                )
                df_rewards.to_csv(
                    f'results/account_rewards_{self.mode}_{self.model_name}_{self.iteration}.csv',
                    index=False,
                )
                plt.plot(self.asset_memory, 'r')
                plt.savefig(
                    f'results/account_value_{self.mode}_{self.model_name}_{self.iteration}.png',
                    index=False,
                )
                plt.close()

            # Add outputs to logger interface
            # logger.record("environment/portfolio_value", end_total_asset)
            # logger.record("environment/total_reward", tot_reward)
            # logger.record("environment/total_reward_pct", (tot_reward /
            # (end_total_asset - tot_reward)) * 100)
            # logger.record("environment/total_cost", self.cost)
            # logger.record("environment/total_trades", self.trades)

            return self.state, self.reward, self.terminal, {}

        else:
            actions = actions * self.hmax  # actions initially is scaled between 0 to 1
            actions = actions.astype(
                int
            )  # convert into integer because we can't by fraction of shares
            if (
                self.turbulence_threshold is not None
                and self.turbulence >= self.turbulence_threshold
            ):
                actions = np.array([-self.hmax] * self.stock_dim)
            begin_total_asset = self.state[0] + sum(
                np.array(self.state[1: (self.stock_dim + 1)]) * np.array(
                    self.state[(self.stock_dim + 1): (self.stock_dim * 2 + 1)])
            )
            # print("begin_total_asset:{}".format(begin_total_asset))

            argsort_actions = np.argsort(actions)
            sell_index = argsort_actions[: np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][: np.where(actions > 0)[0].shape[0]]

            for index in sell_index:
                # print(f"Num shares before: {self.state[index+self.stock_dim+1]}")
                # print(f'take sell action before : {actions[index]}')
                actions[index] = self._sell_stock(index, actions[index]) * (-1)
                # print(f'take sell action after : {actions[index]}')
                # print(f"Num shares after: {self.state[index+self.stock_dim+1]}")

            for index in buy_index:
                # print('take buy action: {}'.format(actions[index]))
                actions[index] = self._buy_stock(index, actions[index])

            self.actions_memory.append(actions)

            # state: s -> s+1
            self.day += 1
            self.data = self.df.loc[self.day, :]
            if self.turbulence_threshold is not None:
                if len(self.df.tic.unique()) == 1:
                    self.turbulence = self.data[self.risk_indicator_col]
                elif len(self.df.tic.unique()) > 1:
                    self.turbulence = self.data[self.risk_indicator_col].values[0]
            self.state = self._update_state()

            end_total_asset = self.state[0] + sum(
                np.array(self.state[1: (self.stock_dim + 1)]) * np.array(
                    self.state[(self.stock_dim + 1): (self.stock_dim * 2 + 1)])
            )
            self.asset_memory.append(end_total_asset)
            self.date_memory.append(self._get_date())
            self.reward = end_total_asset - begin_total_asset
            self.rewards_memory.append(self.reward)
            self.reward = self.reward * self.reward_scaling
            self.state_memory.append(
                self.state
            )  # add current state in state_recorder for each step

        return self.state, self.reward, self.terminal, {}

    def reset(self):
        """
        Reset simulation state.
        """
        # initiate state
        self.state = self._initiate_state()

        if self.initial:
            self.asset_memory = [
                self.initial_amount + np.sum(
                    np.array(self.num_stock_shares) * np.array(
                        self.state[1: 1 + self.stock_dim])
                )
            ]
        else:
            previous_total_asset = self.previous_state[0] + sum(
                np.array(self.state[1: (self.stock_dim + 1)]) * np.array(
                    self.previous_state[(self.stock_dim + 1): (self.stock_dim * 2 + 1)]
                )
            )
            self.asset_memory = [previous_total_asset]

        self.day = 0
        self.data = self.df.loc[self.day, :]
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.terminal = False
        # self.iteration=self.iteration
        self.rewards_memory = []
        self.actions_memory = []
        self.date_memory = [self._get_date()]

        self.episode += 1

        return self.state

    def render(self, mode='human', close=False):
        """
        Render the state of the widget.

        Args:
            mode: type of modelling
            close: closing price
        """
        return self.state

    def _initiate_state(self):
        """
        Create the initial state for the stock.
        """
        if self.initial:
            # For Initial State
            return (
                (
                    [self.initial_amount]
                    + self.data.close.values.tolist()
                    + self.num_stock_shares
                    + sum(
                        (
                            self.data[tech].values.tolist()
                            for tech in self.tech_indicator_list
                        ),
                        [],
                    )
                )
                if len(self.df.tic.unique()) > 1
                else (
                    [self.initial_amount]
                    + [self.data.close]
                    + [0] * self.stock_dim
                    + sum(
                        ([self.data[tech]] for tech in self.tech_indicator_list),
                        [],
                    )
                )
            )
        elif len(self.df.tic.unique()) > 1:
                # for multiple stock
            return (
                [self.previous_state[0]]
                + self.data.close.values.tolist()
                + self.previous_state[
                    (self.stock_dim + 1) : (self.stock_dim * 2 + 1)
                ]
                + sum(
                    (
                        self.data[tech].values.tolist()
                        for tech in self.tech_indicator_list
                    ),
                    [],
                )
            )
        else:
                # for single stock
            return (
                [self.previous_state[0]]
                + [self.data.close]
                + self.previous_state[
                    (self.stock_dim + 1) : (self.stock_dim * 2 + 1)
                ]
                + sum(([self.data[tech]] for tech in self.tech_indicator_list), [])
            )

    def _update_state(self):
        """
        Update state of the dataframe
        """
        if len(self.df.tic.unique()) > 1:
            # for multiple stock
            state = (
                [self.state[0]] + self.data.close.values.tolist() + list(self.state[(
                    self.stock_dim + 1): (self.stock_dim * 2 + 1)]) + sum(
                    (
                        self.data[tech].values.tolist()
                        for tech in self.tech_indicator_list
                    ),
                    [],
                )
            )

        else:
            # for single stock
            state = (
                [self.state[0]] + [self.data.close] + list(self.state[(self.stock_dim + 1): (
                    self.stock_dim * 2 + 1)]) + sum((
                        [self.data[tech]] for tech in self.tech_indicator_list), [])
            )

        return state

    def _get_date(self):
        """
        Get the date of the dataframe
        """
        if len(self.df.tic.unique()) > 1:
            date = self.data.date.unique()[0]
        else:
            date = self.data.date
        return date

    # add save_state_memory to preserve state in the trading process
    def save_state_memory(self):
        """
        Saves state memory in a readable format.
        """
        # date and close price length must match actions length
        date_list = self.date_memory[:-1]
        if len(self.df.tic.unique()) > 1:
            df_date = pd.DataFrame(date_list)
            df_date.columns = ['date']

            state_list = self.state_memory
            df_states = pd.DataFrame(
                state_list,
                columns=[
                    'cash',
                    'Bitcoin_price',
                    'Gold_price',
                    'Bitcoin_num',
                    'Gold_num',
                    'Bitcoin_Disable',
                    'Gold_Disable',
                ],
            )
            df_states.index = df_date.date
                # df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        else:
            state_list = self.state_memory
            df_states = pd.DataFrame({'date': date_list, 'states': state_list})
        # print(df_states)
        return df_states

    def save_asset_memory(self):
        """
        Returns a pandas DataFrame with the date and asset memory data.
        """
        date_list = self.date_memory
        asset_list = self.asset_memory
        return pd.DataFrame({'date': date_list, 'account_value': asset_list})

    def save_action_memory(self):
        """
        Save actions in memory.
        """
        # date and close price length must match actions length
        date_list = self.date_memory[:-1]
        if len(self.df.tic.unique()) > 1:
            df_date = pd.DataFrame(date_list)
            df_date.columns = ['date']

            action_list = self.actions_memory
            df_actions = pd.DataFrame(action_list)
            df_actions.columns = self.data.tic.values
            df_actions.index = df_date.date
                # df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        else:
            action_list = self.actions_memory
            df_actions = pd.DataFrame({'date': date_list, 'actions': action_list})
        return df_actions

    def _seed(self, seed=None):
        """
        Seed the generator with the given seed.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        """
        Get a vector environment and a vector obs of the problem.
        """
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs
