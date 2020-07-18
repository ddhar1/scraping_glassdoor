# Scraping Glassdoor reviews
I'd like to map the reviews I have scrapped to company stock exchange prices and see how reviews fluctuate with price via some sort of dashboard. Also inputting the data into a AWS RDS Postgres file
currently done:

- avg stock price vs avg company review (graph in tableau - time series analysis
- airflow to refresh stock data and call api - get difference between last and current
- 

1. scrapped a two companies' reviews
wip:
2. creating a table in postgres for the files\
3. Make notebook run via command line using Argparse, an application that makes python programs run on command line, or as a docker container (still reading about these options).
4. Use stock exchange API to get data for companies that I scraped. Stock prices would be averaged by month due to the fact that glassdoor reviews are infrequent
5. Unsure how dashboard I would make would look like, but would like to map stock prices to average employee company ratings around the stock price date