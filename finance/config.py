# Defining Directories
DATA_DIR = 'csvs'
TRAINED_MODELS = 'trained_models'
TENSORBOARD_LOG_DIR = 'tb_logdir'
RESULTS = 'results'

# Defining train/val/test dates
TRAIN_START = '2015-01-01'
TRAIN_END = '2019-12-31'

VAL_START = '2020-01-01'
VAL_END = '2021-12-31'

TEST_START = '2022-01-01'
TEST_END = '2022-12-01'

# Defining indicators to implement
INDICATORS = [
    'macd',
    'boll_ub',
    'boll_lb',
    'rsi_30',
    'cci_30',
    'dx_30',
    'close_30_sma',
    'close_60_sma',
    'vr_30',
    'wr_30',
    'atr_30',
    'supertrend',
    'vwma_30',
    'mfi_30',
    'close_30_tema',
]

# Defining Model Parameters
A2C_PARAMS = {'n_steps': 5, 'ent_coef': 0.01, 'learning_rate': 0.0007}
PPO_PARAMS = {
    'n_steps': 2048,
    'ent_coef': 0.01,
    'learning_rate': 0.00025,
    'batch_size': 64,
}
DDPG_PARAMS = {'batch_size': 128, 'buffer_size': 50000, 'learning_rate': 0.001}
TD3_PARAMS = {'batch_size': 100, 'buffer_size': 1000000, 'learning_rate': 0.001}
SAC_PARAMS = {
    'batch_size': 64,
    'buffer_size': 100000,
    'learning_rate': 0.0001,
    'learning_starts': 100,
    'ent_coef': 'auto_0.1',
}
ERL_PARAMS = {
    'learning_rate': 3e-5,
    'batch_size': 2048,
    'gamma': 0.985,
    'seed': 312,
    'net_dimension': 512,
    'target_step': 5000,
    'eval_gap': 30,
    'eval_times': 64,
}
RLlib_PARAMS = {'lr': 5e-5, 'train_batch_size': 500, 'gamma': 0.99}

# API secrets
IB_KEY = ''
IB_SECRET = ''
