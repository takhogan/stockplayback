from Grapher import StockCharter
from AlphaVantage import AlphaVantageInterface
import datetime
from enum import Enum
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# data up to 11/4/2019

class PriceColor(Enum):
    GREEN = 1
    WHITE = 0
    RED = -1


class TradeType(Enum):
    LONG = 1
    SHORT = -1


class Account:
    def __init__(self, id, balance, leverage_level, max_drawdown, max_positions=2):
        self.id = id
        self.balance = balance
        self.leverage_level = leverage_level
        self.max_drawdown = max_drawdown
        self.max_positions = max_positions

    def allocate(self, price):
        max_allowance = self.balance * self.leverage_level
        max_loss = max_allowance * self.max_drawdown
        max_available = (self.balance - max_loss) / self.max_positions
        return int(max_available / price)




class StockTrade:
    def __init__(self, trade_id, entry_price, entry_time, trade_type):
        self.trade_id = trade_id
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.close_price = None
        self.close_time = None
        self.trade_type = trade_type
        self.trade_profit = 0

    def close(self, close_price, close_time):
        self.close_price = close_price
        self.close_time = close_time
        if self.trade_type == TradeType.LONG:
            trade_profit = self.close_price - self.entry_price
        elif self.trade_type == TradeType.SHORT:
            trade_profit = self.entry_price - self.close_price
        else:
            print('invalid TradeType')
            exit(1)

        self.trade_profit = trade_profit
        return self.trade_profit


class PriceAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def get_color(candlestick):
        if candlestick['close'] > candlestick['open']:
            return PriceColor.GREEN
        elif candlestick['close'] < candlestick['open']:
            return PriceColor.RED
        else:
            return PriceColor.WHITE

    def find_flip(self, price_range, pivot_high=None, pivot_low=None):
        pass

    def find_pivots(self, price_range):
        pass

    def find_ranges(self, trading_range, pivot_highs, pivot_lows):
        pass

  

class StockTrader:
    def __init__(self, data):
        self.data = data
        self.last_trade_id = 0
        self.active_trades = []
        self.closed_trades = []

    def enter_trade(self, entry_price, entry_time, trade_type, trade_id=None):
        if trade_id is None:
            trade_id = self.last_trade_id + 1
            self.last_trade_id = trade_id
        new_trade = StockTrade(trade_id, entry_price, entry_time, trade_type)
        self.active_trades.append(new_trade)
        return new_trade

    def find_trade(self, trade_id):
        for trade in self.active_trades:
            if trade.trade_id == trade_id:
                return trade

    def close_trade(self, trade_id, close_price, close_time):
        for trade in self.active_trades:
            if trade.trade_id == trade_id:
                trade.close(close_price, close_time)
                self.closed_trades.append(trade)
                self.active_trades.remove(trade)
                return trade



    def track_trade(self, trade, account, trading_range, trade_charter, pivot_high=None, pivot_low=None):
        end_time = trading_range.index[-1]
        quantity = account.allocate(trade.entry_price)
        if trade.trade_type == TradeType.LONG:
            pivot_timestamp, pivot_high, close_timestamp, close_price = \
                PriceAnalyzer.track_to_exit(trade=trade,
                                            mode='long',
                                            price_range=trading_range,
                                            track_mode='HARD',
                                            trade_charter=trade_charter,
                                            pivot_high=pivot_high,
                                            pivot_low=pivot_low)
            trade_profit = (close_price - trade.entry_price) * quantity
            trade.trade_profit += trade_profit
            trade_charter.add_state_table(time=close_timestamp,
                                          state_table=[
                                              'ph:' + str(pivot_high),
                                              'pl:' + str(pivot_low),
                                              'closed',
                                              'p/l:' + str(trade_profit),
                                              'cumul:' + str(trade.trade_profit)
                                          ])
            if close_timestamp < end_time:
                trade.trade_type = TradeType.SHORT
                trade.entry_price = close_price
                self.track_trade(trade=trade,
                                 account=account,
                                 trading_range=trading_range[pivot_timestamp:],
                                 trade_charter=trade_charter,
                                 pivot_high=pivot_high,
                                 pivot_low=None)
        else:
            pivot_timestamp, pivot_low, close_timestamp, close_price = \
                PriceAnalyzer.track_to_exit(trade=trade,
                                            mode='short',
                                            price_range=trading_range,
                                            track_mode='HARD',
                                            trade_charter=trade_charter)
            trade_profit = (trade.entry_price - close_price) * quantity
            trade.trade_profit += trade_profit
            trade_charter.add_state_table(time=close_timestamp,
                                          state_table=[
                                              'ph:' + str(pivot_high),
                                              'pl:' + str(pivot_low),
                                              'closed',
                                              'p/l:' + str(trade_profit),
                                              'cumul:' + str(trade.trade_profit)
                                          ])
            if close_timestamp < end_time:
                trade.trade_type = TradeType.LONG
                trade.entry_price = close_price
                self.track_trade(trade=trade,
                                 account=account,
                                 trading_range=trading_range[pivot_timestamp:],
                                 trade_charter=trade_charter,
                                 pivot_high=None,
                                 pivot_low=pivot_low)



    def track_trades(self, account, trading_range=None):
        if trading_range is None:
            trading_range = self.data

        trade_charter = StockCharter(trading_range)
        for trade in self.active_trades:
            self.track_trade(trade=trade,
                             account=account,
                             trading_range=trading_range,
                             trade_charter=trade_charter)

        trade_charter.show()


    def trade_day(self, account, year, month, day):
        self.trade_range(account=account,
                         start_time=datetime.datetime(year, month, day, 0, 0, 0),
                         end_time=datetime.datetime(year, month, day, 16, 0, 0))


    def trade_range(self, account, start_time=None, end_time=None):
        if start_time is not None and end_time is None:
            trading_range = self.data[start_time:]
        elif start_time is None and end_time is not None:
            trading_range = self.data[:end_time]
        elif start_time is not None and end_time is not None:
            trading_range = self.data[start_time:end_time]
        else:
            trading_range = self.data

        direction = PriceAnalyzer.get_color(trading_range.iloc[0])
        range_charter = StockCharter(trading_range)
        init_closing_price = trading_range.loc[trading_range.index[0], 'close']
        if direction == PriceColor.GREEN:
            self.enter_trade(entry_price=init_closing_price,
                             entry_time=trading_range.index[0],
                             trade_type=TradeType.LONG)
            # range_charter.add_entry(price=init_closing_price,
            #                         time=trading_range.index[0],
            #                         text='Long at $' + str(init_closing_price))
        elif direction == PriceColor.RED:
            self.enter_trade(entry_price=init_closing_price,
                             entry_time=trading_range.index[0],
                             trade_type=TradeType.SHORT)
            # range_charter.add_entry(price=init_closing_price,
            #                         time=trading_range.index[0],
            #                         text='Short at $' + str(init_closing_price))
        pa = PriceAnalyzer()
        pivots, fragmentation, similarity = pa.find_pivots(trading_range)
        # range_charter.add_indicator(x=fragmentation.index,
        #                             y=fragmentation['magnitude'])
        pivot_highs = pivots['pivot_high'].dropna()
        pivot_lows = pivots['pivot_low'].dropna()
        fragmentation.dropna(inplace=True)
        similarity.dropna(inplace=True)
        # print(fragmentation)
        # fragmentation['magnitude'].hist()
        # plt.show()

        # exit(0)
        # print(pivot_highs)
        range_charter.add_trace(x=pivot_highs.index, y=pivot_highs)
        range_charter.add_trace(x=pivot_lows.index, y=pivot_lows)
        range_charter.add_indicator(x=fragmentation.index, y=fragmentation['magnitude'])
        range_charter.add_indicator(x=similarity.index, y=similarity['similarity'])
        range_charter.show()

        exit(0)
        self.track_trades(account=account,
                          trading_range=trading_range)
        # range_charter.show()




if __name__ == '__main__':
    data_loader = AlphaVantageInterface()
    stock_data = data_loader.load_bars('FB', reload=False)
    # StockCharter(stock_data).show()


    stock_trader = StockTrader(stock_data)
    end_day = stock_data.index[-1].date()

    day_trading_account = Account('day', 100000, 2, 0.1, 4)
    # stock_trader.trade_day(day_trading_account, 2019, 11, 7)
    # stock_trader.trade_range(account=day_trading_account,
    #                          start_time=datetime.datetime(end_day.year, end_day.month, end_day.day, 0, 0, 0),
    #                          end_time=stock_data.index[-1])
    stock_trader.trade_range(account=day_trading_account,
                             start_time=None,
                             end_time=None)

