from __future__ import annotations

from finrl.meta.env_stock_trading.env_stock_papertrading import AlpacaPaperTrading
from finrl.test import test


def trade(
    start_date,
    end_date,
    ticker_list,
    data_source,
    time_interval,
    technical_indicator_list,
    drl_lib,
    env,
    model_name,
    API_KEY,
    API_SECRET,
    API_BASE_URL,
    trade_mode="backtesting",
    if_vix=True,
    **kwargs,
):
    """
    Trading mode is either ""test"" or ""trade_mode == ""backtest"".

    Args:
        start_date: write your description
        end_date: write your description
        ticker_list: write your description
        data_source: write your description
        time_interval: write your description
        technical_indicator_list: write your description
        drl_lib: write your description
        env: write your description
        model_name: write your description
        API_KEY: write your description
        API_SECRET: write your description
        API_BASE_URL: write your description
        trade_mode: write your description
        if_vix: write your description
    """
    if trade_mode == "backtesting":
        # use test function for backtesting mode
        test(
            start_date,
            end_date,
            ticker_list,
            data_source,
            time_interval,
            technical_indicator_list,
            drl_lib,
            env,
            model_name,
            if_vix=True,
            **kwargs,
        )

    elif trade_mode == "paper_trading":
        # read parameters
        try:
            net_dim = kwargs.get("net_dimension", 2**7)  # dimension of NNs
            cwd = kwargs.get("cwd", "./" + str(model_name))  # current working directory
            state_dim = kwargs.get("state_dim")  # dimension of state/observations space
            action_dim = kwargs.get("action_dim")  # dimension of action space
        except:
            raise ValueError(
                "Fail to read parameters. Please check inputs for net_dim, cwd, state_dim, action_dim."
            )

        # initialize paper trading env
        paper_trading = AlpacaPaperTrading(
            ticker_list,
            time_interval,
            drl_lib,
            model_name,
            cwd,
            net_dim,
            state_dim,
            action_dim,
            API_KEY,
            API_SECRET,
            API_BASE_URL,
            technical_indicator_list,
            turbulence_thresh=30,
            max_stock=1e2,
            latency=None,
        )

        # AlpacaPaperTrading.run()  # run paper trading
        paper_trading.run()
        # bug fix run is a instance function not static

    else:
        raise ValueError(
            "Invalid mode input! Please input either 'backtesting' or 'paper_trading'."
        )
