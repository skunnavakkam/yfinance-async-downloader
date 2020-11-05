# yfinance-async-downloader: Faster stock market queries
The [yfinance](https://github.com/ranaroussi/yfinance) module by ranarrousi was slow for large stock market queries, and would usually be the larget time requirement in programs. yfinance-async-downloader solves that problem by working on similar grounds to yfinance, but getting the data cocurrently with asyncio in python. 
## Quick Start
For most purposes, the download module will suffice. The download module lacks some of the more niche functionality of yfinance such as financials, quarterly financial, major holders etc, since those have to be scraped. It only provides the dividends, splits, and history per stock (if it can be found).

```python
data = download(['AAPL', 'MSFT', 'AMZN], datetime.datetime(2020,1,1), datetime.datetime.today(), '1d')
history_data = data['History']
dividend_data = data['Dividends']
split_data = data['Splits']

history_data['AAPL']
# data for AAPL history

dividend_data['MSFT']
# data for MSFT dividends

split_data['AMZN']
# data for AMZN splits
```
## Speed
*All information as of November 5 2020*

Speed is tested against yfinance's download function, which uses threading for the most fair comparision. Speed will be measured using time.perf_counter().
Will be conducted in four tests. One stock (AAPL), a list of the 30 largest stocks, the S&P 500 component stocks, and the Russell 2000 index. Tests will be conducted on a computer running the latest version of Windows 10 with a i7 7700k.

### 1 Stock
Time taken to download data for AAPL from November 4 2019 to November 4 2020, rounded to two decimal places

yfinance:
```
0.42 seconds
```
async-downloader:
```
0.40 seconds
```

### 30 Stocks
Time taken to download the largest 10 stocks by market cap over the same period

yfinance:
```
1.15 seconds
```
async-downloader:
```
0.57 seconds
```

### 500 Stocks
Time taken to download the entire S&P 500 over the same period

yfinance:
```
13.82 seconds
```
async-downloader:
```
8.69 seconds
```

### Russell 2000
Time taken to download 2000 stocks over the same period

yfinance:
```
263.23 seconds
```
async-downloader:
```
15.03 seconds
```
