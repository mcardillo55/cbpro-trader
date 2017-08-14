# gdax-trader

gdax-trader is a bot to automate trading on the GDAX cryptocurrency exchange. It is based around the ta-lib and gdax-python libraries, allowing easy trading based on technical analysis indicators.

Most of the code is currently written to trade Bitcoin (BTC), but can be tweaked to trade any cryptocurrency currently supported by GDAX. It is the eventual goal to be able to track all GDAX cryptocurrencies and trade whichever has the best opportunity at the moment.

## Requirements

You can install most requirements with 

`pip install -r ./requirements.txt`

Currently, we're using the upstream version of the gdax-python library, so you will need to do

`pip uninstall gdax` then

`pip install git+git://github.com/danpaquin/gdax-python.git`. 

Also note that the TA-Lib python library is actually a wrapper for the ta-lib C library, so you will need to install that before. See the "Dependencies" section on https://github.com/mrjbq7/ta-lib for more information on that.

## Configuration

Copy config.py.sample to config.py and include your KEY, SECRET, and PASSPHRASE values from your GDAX API key.

INTERFACE can be set to `curses` which is an ncurses display of balances, indicator values, recent candlesticks and trades and current open orders or `debug` which will print the same infromation to the console, line-by-line, as it is available.

I'm throwing around an idea of making a local web frontend, maybe in React or something similar, to better visualize the current data recorded by the bot.

## Tweaking indicators and trade logic

If you're handy with Python, any indicators from TA-Lib can be added, as desired. Trade logic can also obviously be modified as well.

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

When issuing a buy order, be sure to set `self.buy_flag = True` and `self.sell_flag = False` before starting the buy order thread. This is to be sure that if there is a sell order pending, it will be cancelled and the sell thread will be closed. The same obviously holds true when issueing a sell order.
