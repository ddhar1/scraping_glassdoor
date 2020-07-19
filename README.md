# Understanding the correlation between Company Stock Prices and Company Reviews

**This project is abandoned due to Glassdoor's terms**

The goal of this project is to ELT process that periodically scrapes company review data from glassdoor, as well as extracts stock price data from an API as well as company financial information from data.world datasets, stores it in S3 as parquet so a backup is stored, while placing the data onto Redshift. In Redshift, I want to perform data modeling with dbt, and display the data using Elastic Beanstalk and metadata-store in order to visualize the data

## Part 1: Initial ELT
More about the structure about this project and the requirements of each aspect
* need to use **parameter store** in aws for the api keys, glassdoor credentials, redshift quering

*  **AWS EC2** instance (anything with AWS CLI readily available). This would be useful for running the intial ETL, but could be closed after
	* one issue is that some website block aws from scraping. 
*  Redshift instance
	* something that can handle OLAP queries is ideal due to types of data processing I would like to perform on this dataset
	* It probably doesn't need to be scaled often. The only dataset I can see growing fairly quickly is the stock prices dataset. For the purpose of this analysis, this dataset coul dbe on a ]weekly basis. 
	* a schema for staging, and prod
	1. A quick python program that queries Redshift to create initial schemas is necessary. This could be also be done in AWS management consol but the script helps with documentation and visibility

### Initial ETL
1. Glassdoor scraper python that selects companies and queries 
	* About the scraper
		a) Uses Selenium read run javascript and scrape appropriate HTML
		b) Inputs: company URL, credentials of user: username, password, before date, after date, company name to use in the file
		c) Uses lengthy wait times and no multithreading to not overwhelm the site
	* Uses boto3 to load output data as a parquet in S3. Data can be partioned by company. Possibly by date as well, but more analysis would need to be performed on distribution of dates, since I imagine it's pretty inconsistented

2. Program that queries Stock price and data.world
	A. Queries Stock Price API, loads it into AWS as parquet, by company, by month, most likely
	B. Queries data world and loads it into AWS as parquet. I don't expect this to be partitioned since it's so small. This dataset updates once a year

3. Program that copies parquets and places them in Redshift

### Automatic ETL updates
Use AWS Lambda(?), cloudwatch in order to run these.

Both would require quering the tables respective data in redshift in order get the last date loaded. This data would be passed into the API/glassdoor scraper function so that data would not be collected before this date (don't redo things!)
Would probably need to store company's respective URL in a database (unsure if it's best practice to put into dev schema in redshift or put in small rds)

* **Parameter Store** would have to be used for storing the aws redshift DB credentials, API Keys, Glassdoor Credentials

1. Glassdoor scraper could be potentially placed on AWS Lambda. 
	* Yes the chrome driver is required, but a driver on AWS Lambda [has been done before](https://medium.com/hackernoon/running-selenium-and-headless-chrome-on-aws-lambda-layers-python-3-6-bd810503c6c3). Selenium would need to be loaded into the aws lambda environment. 
	* Again would be concerned if AWS would be blocked.\
	* if the first option is an issue and legality wasn't a problem, could just use a regular virtual machine that runs monthly, with cron? Or nohup a script monthly, but there's cognitive laod
	* glassdoor possibly changes their site a lot. need to think about enough checks 
	* run data quality checks at end (or at least 'first page' of company's data about to be queried)
2. Lambda function that queries Stock price API 
	* requests apparently can be imported with `from botocore.vendored import requests`? Have previous uploaded zip files of requests module
	* scheduled with cloudwatch
	* run dataquality checks at end

### To think about:
* I stil need to think further about how dbt refreshes would be run, or if they even need to.
Of course this could depend on the program's visibility in a company (how many ppl will use it). For the purposes of the project, probably not a lot or at all :)
Apparently metabase may **[cache queries](https://github.com/metabase/metabase/issues/10745)**. One could potentially place a dbt docker image on fargate. But caching sounds much easier given the visibility of this database/
* how hard is it for someone to add a new company to the list? What are the painpoints?
