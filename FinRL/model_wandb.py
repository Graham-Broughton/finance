import pprint
import time

import numpy as np
import pandas as pd
import wandb
from stable_baselines3 import A2C
from stable_baselines3 import DDPG
from stable_baselines3 import PPO
from stable_baselines3 import SAC
from stable_baselines3 import TD3
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.noise import OrnsteinUhlenbeckActionNoise
from stable_baselines3.common.vec_env import DummyVecEnv
from wandb.integration.sb3 import WandbCallback

from finrl import config
from finrl.meta.preprocessor.preprocessors import data_split
# from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
MODELS = {"a2c": A2C, "ddpg": DDPG, "td3": TD3, "sac": SAC, "ppo": PPO}

MODEL_KWARGS = {x: config.__dict__[f"{x.upper()}_PARAMS"] for x in MODELS.keys()}

NOISE = {
    "normal": NormalActionNoise,
    "ornstein_uhlenbeck": OrnsteinUhlenbeckActionNoise,
}

class DRLAgent_SB3:
  def __init__(self,env,run):
    self.env = env
    # self.run = wandb.init(reinit=True,
    #       project = 'finrl-sweeps-sb3',
    #       sync_tensorboard = True,
    #       save_code = True
    #   )
    self.run = run
  def get_model(
      self,
      model_name,
      policy_kwargs=None,
      model_kwargs=None,
      verbose=1,
      seed=None,
  ):
      if model_name not in MODELS:
          raise NotImplementedError("NotImplementedError")

      if model_kwargs is None:
          model_kwargs = MODEL_KWARGS[model_name]

      if "action_noise" in model_kwargs:
          n_actions = self.env.action_space.shape[-1]
          model_kwargs["action_noise"] = NOISE[model_kwargs["action_noise"]](
              mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions)
          )
      print(model_kwargs)

      model = MODELS[model_name](
          policy='MlpPolicy',
          env=self.env,
          tensorboard_log=f"runs/{self.run.id}",
          verbose=verbose,
          policy_kwargs=policy_kwargs,
          seed=seed,
          **model_kwargs,
      )
      return model

  def train_model(self, model,total_timesteps):
    model = model.learn(
        total_timesteps=total_timesteps,
        callback = WandbCallback(
            gradient_save_freq = 100, model_save_path = f"models/{self.run.id}",
            verbose = 2
        ),
    )

    return model
  @staticmethod
  def DRL_prediction_load_from_file(run , model_name, environment,val_or_test='val'):
      if model_name not in MODELS:
          raise NotImplementedError("NotImplementedError, Pass correct model name")
      try:
          # load agent
          model = MODELS[model_name].load(f"models/{run.id}/model.zip") #print_system_info=True
          print("Successfully load model", f"models/{run.id}")
      except BaseException:
          raise ValueError("Fail to load agent!")

      # test on the testing env
      state = environment.reset()
      episode_returns = list()  # the cumulative_return / initial_account
      episode_total_assets = list()
      episode_total_assets.append(environment.initial_total_asset)
      done = False
      while not done:
          action = model.predict(state)[0]
          state, reward, done, _ = environment.step(action)

          total_asset = (
              environment.amount
              + (environment.price_ary[environment.day] * environment.stocks).sum()
          )
          episode_total_assets.append(total_asset)
          episode_return = total_asset / environment.initial_total_asset
          episode_returns.append(episode_return)

      def calculate_sharpe(df):
        df['daily_return'] = df['account_value'].pct_change(1)
        if df['daily_return'].std() !=0:
          sharpe = (252**0.5)*df['daily_return'].mean()/ \
              df['daily_return'].std()
          return sharpe
        else:
          return 0

      print("episode_return", episode_return)
      print("Test Finished!")
      sharpe_df = pd.DataFrame(episode_total_assets,columns=['account_value'])
      sharpe = calculate_sharpe(sharpe_df)
      if val_or_test == "val":
        wandb.log({"Val sharpe":sharpe})
      elif val_or_test == "test":
        wandb.log({"Test sharpe":sharpe})
        print(f'Test Sharpe for {run.id} is {sharpe}')
      # run.finish()
      return sharpe, episode_total_assets
