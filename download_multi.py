import datetime
import pandas as pd
import asyncio


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()  # getting the response from the URL


async def download_list(tickers: list, start_date: datetime.datetime, end_date: datetime.datetime, interval: str):
    from aiohttp import ClientSession  # importing it in the function helps speed things up a little bit

    # processing the arguments so this step won't be repeated in the loop
    _period_one = int(start_date.timestamp())
    _period_two = int(end_date.timestamp())
    _interval = interval.lower()

    _tickers = []  # Later holds list of capitalized tickers from args. Needed for making the data easier to parse etc.

    tasks = []  # a list of async tasks

    # Defining one session rather than one per ticker for less resource utilization
    async with ClientSession() as session:
        for i in tickers:
            # processing tickers
            _ticker = i.upper().replace('.', '-')
            _tickers.append(_ticker)

            # Yahoo!Finance gives JSON when you call the right URL. Dir JSON Example for Examples
            _base_url = 'https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}' \
                        '&interval={}&events=div%2Csplit&includeAdjustedClose=true'.format(_ticker, _period_one,
                                                                                           _period_two, _interval)

            # makes an async task and adds it to the task list
            task = asyncio.ensure_future(fetch(_base_url, session))
            tasks.append(task)

        # allows tasks to be run concurrently
        responses = await asyncio.gather(*tasks)

        # returns list of capitalized tickers and gathered tasks
        return responses, _tickers


def parse_yahoo_json(json_text, ticker):
    from json import loads  # importing in function to make lookups faster

    # parsing the returned data
    json_dict = loads(json_text)['chart']

    # checking if there is data and there are no errors
    if json_dict['error'] is None and 'timestamp' in json_dict['result'][0]:

        json_dict = json_dict['result'][0]

        # isolates the data needed for price history
        _timestamp = json_dict['timestamp']
        _open = json_dict['indicators']['quote'][0]['open']
        _close = json_dict['indicators']['quote'][0]['close']
        _volume = json_dict['indicators']['quote'][0]['volume']
        _high = json_dict['indicators']['quote'][0]['high']
        _low = json_dict['indicators']['quote'][0]['low']
        _adj_close = json_dict['indicators']['adjclose'][0]['adjclose']

        # converting all timestamps into datetime.datetime objects.
        count = 0
        for i in _timestamp:
            _timestamp[count] = datetime.datetime.fromtimestamp(i)
            count += 1

        # creates a Pandas DataFrame from the price history information
        _history_DF = pd.DataFrame(
            {'Date': _timestamp, 'Adj. Close': _adj_close, 'Close': _close, 'Open': _open, 'High': _high, 'Low': _low,
             'Volume': _volume})

        # setting index to Date rather than numerical index
        _history_DF = _history_DF.set_index('Date')

        # if no events (div, splits) exist, it doesn't for
        _events = None

        if 'events' in json_dict:
            _events = json_dict['events']

        _dividends_DF = None
        _splits_DF = None

        # only tries to get dividend and split information if event information exists
        if _events is not None:

            # getting dividend information if dividend information exists
            if 'dividends' in _events:
                # making lists of the dates and amounts of the dividends
                _dividends = _events['dividends']
                _dividend_amount = list()
                _dividend_dates = list()
                for d in _dividends:
                    i = int(d)
                    _dividend_dates.append(datetime.datetime.fromtimestamp(i))
                    _dividend_amount.append(_dividends[d]['amount'])

                # making DataFrame and setting index to 'Dates'
                _dividends_DF = pd.DataFrame({'Dates': _dividend_dates, 'Amount': _dividend_amount})
                _dividends_DF = _dividends_DF.set_index('Dates')

            # pretty much repeats the same thing for splits
            if 'splits' in _events:
                _splits = _events['splits']
                _splits_dates = list()
                _splits_numerators = list()
                _splits_denominators = list()
                for d in _splits:
                    i = int(d)
                    _splits_dates.append(datetime.datetime.fromtimestamp(i))
                    _splits_numerators.append(_splits[d]['numerator'])
                    _splits_denominators.append(_splits[d]['denominator'])
                _splits_DF = pd.DataFrame(
                    {'Dates': _splits_dates, 'Numerators': _splits_numerators, 'Denominator': _splits_denominators})
                _splits_DF = _splits_DF.set_index('Dates')

        # returns history, splits, dividends. splits and dividends default to None if no data is available
        return _history_DF, _splits_DF, _dividends_DF

    # if no data is available for a ticker, it prints ticker: No data found ...
    elif json_dict['error'] is None:
        print('{}:'.format(ticker), 'No data found for this date range, symbol may be delisted')

    # if a problem arises with any one ticker, it prints ticker: problem
    elif 'description' in json_dict['error']:
        print('{}:'.format(ticker), json_dict['error']['description'])

    # raises error if Yahoo!Finance API is down
    elif "Will be right back" in json_text:
        raise Exception('Error in Yahoo!Finance API')