# gdax-trader

gdax-trader is a bot to automate trading on the GDAX cryptocurrency exchange. It is based around the ta-lib and gdax-python libraries, allowing easy trading based on technical analysis indicators.

The bot can monitor and trade any ticker supported by GDAX, and will even trade between cryptocurrencies if the opportunity is better.

## Disclaimer

This bot is still in early stages and may have bugs. The strategies also need major reworking. **Do not use with any money you are not 100% willing to lose.**

## Requirements

You can install most requirements with 

`pip install -r ./requirements.txt`

Note that it is currently pointing to a custom version of the gdax-python library until I can push my OrderBook changes upstream.

Also note that the TA-Lib python library is actually a wrapper for the ta-lib C library, so you will need to install that before. See the "Dependencies" section on https://github.com/mrjbq7/ta-lib for more information on that.

## Configuration

Copy config.yml.sample to config.yml and include your `key`, `secret`, and `passphrase` values from your GDAX API key.

Set `live` to `yes` **only if** you want the bot to execute **actual trades.** The bot will still collect data and calculate indicators when LIVE is set to FALSE.

In config.yml you can list as many periods as you would like under the periods section. Periods will be used for trading logic only if their `trade:` attribute is set to `yes`, otherwise they are just used for gathering indicator data.

There is experimental support for 'meta' periods, which can be used for comparing 2 products that do not currently have a GDAX trading pair, by setting the `meta:` attribute to `yes` in the period description. The only real use case for this right now is LTC-ETH. Trading on meta periods is not yet supported (work in progress).

`frontend` can be set to `curses` which is an ncurses display of balances, indicator values, recent candlesticks and trades and current open orders or `debug` which will print the same infromation to the console, line-by-line, as it is available. `debug` tends to fall behind in development, as it's mostly used for debugging (obviously).

I'm throwing around an idea of making a local web frontend, maybe in React or something similar, to better visualize the current data recorded by the bot.

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
