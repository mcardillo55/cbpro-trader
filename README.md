# cbpro-trader

cbpro-trader is a bot to automate trading on the Coinbase Pro cryptocurrency exchange. It is based around the ta-lib and coinbasepro-python libraries, allowing easy trading based on technical analysis indicators.

The bot can monitor and trade any ticker supported by Coinbase Pro, and will even trade between cryptocurrencies if the opportunity is better.

## Disclaimer

This bot is still in early stages and may have bugs. The strategies also need major reworking. **Do not use with any money you are not 100% willing to lose.**

## Installation
### Docker

A docker-compose file is included to try to ease installation.

If you are using the `web` frontend, you can simply run `docker-compose up` and then visit the URL provided by the frontend server.

If you are using the `curses` or `debug` frontends, you can run

`docker-compose build cbpro`
`docker run -it cbpro-trader_cbpro -v $ABSOLUTE_PATH_TO_PROJECT/cbpro-trader/cbpro-trader/daemon/:/cbpro-trader/:Z`

to build and run the image, making sure to replace the absolute path of the project, then`python3 ./cbpro-trader.py` to start the bot

You will need to run `docker-compose up --build` if you change the config after the initial build.

### Manual

You can install most requirements with

`cd ./cbpro-trader`
`pip install -r ./requirements.txt`

then run with

`python3 ./cbpro-trader.py`

Note that it is currently pointing to a custom version of the coinbasepro-python library until I can push my OrderBook changes upstream.

Also note that the TA-Lib python library is actually a wrapper for the ta-lib C library, so you will need to install that before. See the "Dependencies" section on https://github.com/mrjbq7/ta-lib for more information on that.

## Configuration

Copy config.yml.sample to config.yml and include your `key`, `secret`, and `passphrase` values from your Coinbase Pro API key.

| Name         | Type    | Description                                                                      |
| ------------ | ------- | -------------------------------------------------------------------------------- |
| key          | string  | Coinbase API key                                                                 |
| secret       | string  | Coinbase API secret                                                              |
| passphrase   | string  | Coinbase API passphrase                                                          |
| sandbox      | boolean | Set to 'yes' to use Coinbase sandbox servers (for testing)                       |
| live         | boolean | Set to 'yes' to to toggle live trading                                           |
| frontend     | string  | Which frontend to use - 'console', 'web' or 'debug'. See below for more info.    |
| web_config   | boolean | Set to 'yes' to allow setting config from the web API                            |
| logging      | boolean | Set to 'yes' to add additional logging to debug.log file                         |
| fiat         | string  | Which fiat currency to use - e.g. 'USD' or 'EUR'                                 |
| max_slippage | float   | Max percentage change in limit orders before executing a market order            |
| periods      | list    | A YAML list of periods, each including the options listed in the periods section |

For each period in the `periods` list, include the following options

| Name    | Type    | Description                                                                    |
| ------- | ------- | ------------------------------------------------------------------------------ |
| name    | string  | The display name of the period                                                 |
| product | string  | The Coinbase product to trade                                                  |
| length  | integer | The period length in minutes                                                   |
| trade   | boolean | Set to 'yes' to trade this period                                              |
| meta    | boolean | Set to 'yes' if this is a 'meta' product (one that does not exist on Coinbase) |

Set `live` to `yes`  **only if** you want the bot to execute **actual trades.** The bot will still collect data and calculate indicators when `live` is set to `no`. You may also wish to test functionality with a Coinbase Pro sandbox API key first.

In config.yml you can list as many periods as you would like under the periods section. Periods will be used for trading logic only if their `trade:` attribute is set to `yes`, otherwise they are just used for gathering indicator data.

There is experimental support for 'meta' periods, which can be used for comparing 2 products that do not currently have a Coinbase Pro trading pair, by setting the `meta:` attribute to `yes` in the period description. The only real use case for this right now is LTC-ETH. Trading on meta periods is not yet supported (work in progress).

`frontend` can have the following values
* `web` - a web based frontend to be viewed in your web browser (WORK IN PROGRESS)
* `curses` - an ncurses display of balances, indicator values, recent candlesticks and trades and current open orders or `debug` which will print the same infromation to the console, line-by-line, as it is available.
* `debug` used for debugging (obviously).

## Tweaking indicators and trade logic

I'm currently working on making indicators and trade strategies more configurable, but if you're handy with Python, any indicators from TA-Lib can be added, as desired. Trade logic can also obviously be modified as well.

### Design

The IndicatorSubsystem class contains several methods to calculate indicators. Simple ones are already included, such as `calculate_macd()` and `calculate_obv()`.

These methods write to the dictionary `IndicatorSubsystem.current_indicators` which is eventually used by `TradeEngine.determine_trades()` to determine if the bot should trade.

### Adding indicators

To add a new indicator, first create the new method, following the naming convention. For example, if adding Simple Moving Average (SMA), `calculate_sma()`

In the new method, you will probably want to use TA-LIB to calculate the indicator. Refer to http://mrjbq7.github.io/ta-lib/  for API documentation. For our example:

`sma = talib.SMA(closing_prices, timeperiod=10)`

Note that `closing_prices` and  `volumes` are already available in the IndicatorSubsystem.

Now, just add the most recent of this calculated value to the `current_indicators` dictionary, so that it is available to `TradeEngine`. You will need to add the indicator to the correct key, determined by `period_name` as well. This is to support multiple periods.

`self.current_indicators[period_name]['sma'] = sma[-1]`

### Modifying trade logic

Trade logic can obviously be modified as desired. Just make your decisions in `TradeEngine.determine_trades()`.

`TradeEngine.determine_trades()` has access to the `IndicatorSubsystem.current_indicators` as `indicators`, as was discussed earlier.

When issuing a buy order, be sure to set `product.buy_flag = True` and `product.sell_flag = False` before starting the buy order thread. This is to be sure that if there is a sell order pending, it will be cancelled and the sell thread will be closed. The same obviously holds true when issueing a sell order.
