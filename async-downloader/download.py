from datetime import datetime as dt
import asyncio
from download_multi import *


# wrapping everything in a synchronous function for ease of use (downloads and parses)
def download(tickers: list, start_date: dt, end_date: dt, interval: str):

    # getting the data asynchronously
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(download_list(tickers, start_date, end_date, interval))
    stock_data, _tickers = loop.run_until_complete(future)

    # dictionaries of {ticker: data}
    _history_dict = dict()
    _dividend_dict = dict()
    _splits_dict = dict()

    for d, s in zip(stock_data, _tickers):
        # gets data for stock and stock data
        data = parse_yahoo_json(d, s)

        # adding data to dictionaries with error catching
        try:
            _formatted_history = data[0]
            if _formatted_history is not None:
                _history_dict[s] = _formatted_history
        except:
            pass

        try:
            _formatted_dividends = data[1]
            if _formatted_dividends is not None:
                _dividend_dict[s] = _formatted_dividends
        except:
            pass

        try:
            _formatted_splits = data[1]
            if _formatted_splits is not None:
                _splits_dict[s] = _formatted_splits
        except:
            pass

    _return_dict = {'History': _history_dict, 'Dividends': _dividend_dict, 'Splits': _splits_dict}

    return _return_dict
