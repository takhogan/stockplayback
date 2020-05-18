import requests
from Bar import Bar
import json
import os
import pandas as pd
import time
import datetime
import glob
api_key = 'W8HKHR7LMOMNJETX'
# api_key = 'demo'

def clean_dir():
    symbols = pd.read_csv('symbols.csv')['symbol']
    symbols_dict = {value: key for key, value in symbols.to_dict()['symbol'].items()}
    for file in glob.glob('data/*.csv'):
        if not os.path.splitext(os.path.basename(file))[0] in symbols_dict:
            print('deleting: ' + file)
            os.remove(file)


class AlphaVantageInterface:
    def __init__(self):
        pass

    def load_bars(self, symbol, reload):
        query = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + symbol + '&interval=5min&apikey=' + api_key
        symbol_csv_filename = 'data/' + symbol + '.csv'
        if reload:
            json_query = 'request not completed ' + symbol
            try:
                json_query = requests.get(query).json()
                time_series = json_query["Time Series (5min)"]
            except (KeyError, json.decoder.JSONDecodeError):
                print(json_query)
                if not bool(json_query):
                    print('OTC Stock')
                    return {}
                elif 'Error Message' in json_query:
                    return json_query
                return None
            time_series = pd.DataFrame.from_dict(time_series).T
            new_col_labels = ['open', 'high', 'low', 'close', 'volume']
            time_series.rename(mapper={time_series.columns[name_index]: new_col_labels[name_index]
                                       for name_index in range(0, len(new_col_labels))}, inplace=True, axis=1)
            time_series.index = pd.to_datetime(time_series.index)
            time_series = time_series.reindex(index=time_series.index[::-1])

            if os.path.exists(symbol_csv_filename):
                prev_time_series = pd.read_csv(symbol_csv_filename)
                prev_time_series.set_index(prev_time_series.columns[0], inplace=True)
                prev_time_series.index = pd.to_datetime(prev_time_series.index)

                last_timestamp = prev_time_series.index[-1]
                time_series = time_series.loc[last_timestamp:]
                if time_series.index[0] == last_timestamp:
                    if time_series.shape[0] > 1:
                        time_series = time_series.iloc[1:]
                    else:
                        time_series = pd.DataFrame([])
                time_series = prev_time_series.append(time_series)
            time_series.to_csv(symbol_csv_filename)
            # print(time_series)
            # print(time_series.index)

        else:
            time_series = pd.read_csv(symbol_csv_filename)
            time_series.set_index(time_series.columns[0], inplace=True)
            time_series.index = pd.to_datetime(time_series.index)
        return time_series

    def load_all(self, start_from=None, reload=False):
        symbols = pd.read_csv('symbols.csv')['symbol']
        joint_symbol_df = None
        for symbol in symbols:
            if start_from is not None:
                if symbol != start_from:
                    continue
                start_from = None
            print(symbol)
            bar_result = interface.load_bars(symbol, reload=reload)
            while bar_result is None:
                now_time = datetime.datetime.now()
                end_time = now_time + datetime.timedelta(minutes=1)
                print('waiting until ' + str(end_time))
                time.sleep(int((end_time - now_time).total_seconds()) + 5)
                bar_result = interface.load_bars(symbol, reload=True)
            bar_result.rename(mapper={bar_result.columns[col_index]:symbol + '_' + bar_result.columns[col_index]
                                      for col_index in range(0, len(bar_result.columns))},
                              axis=1,
                              inplace=True)
            if joint_symbol_df is None:
                joint_symbol_df = bar_result
            else:
                joint_symbol_df = joint_symbol_df.join(bar_result, how='outer')
        return joint_symbol_df


if __name__ == '__main__':
    interface = AlphaVantageInterface()
    interface.load_all(reload=True)
