# Reinforcement Learning Trading Bot

This project is still in its infancy so many of these ideas are either non-existent or lacking in implementation. A good portion of it is taken from [this repo](https://github.com/AI4Finance-Foundation/FinRL) except there were quite a few ways to improve it. For example, there were areas where they did not implement vectorization, there is some dead end code that needed to be cleaned up and where appropriate, polars will be used instead of pandas to further improve effeciency.

The idea for this project is to have a fully automated trading bot that not only uses stock OHLCV data for its predictions, but implements the sentiment towards the stocks as well by using an NLP model and webscraping. It will also automatically detect when there is a market regime shift and change its trading strategy accordingly. Scraping the prices each training routine would be very cost prohibitive so it will store the various pieces of information in a database - SQL style for the price data and NoSQL for the web scraped news.

The model itself will be implemented using the gym library and stable-baselines3 or elegantrl for state-of-the-art RL models.
