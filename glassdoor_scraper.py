import re
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

cols_to_check = [ 'date', 'title', 'company_stars', 'work_life_stars', 'author_employee_title', 'author_location']

company_review_urls =  ['https://www.glassdoor.com/Reviews/Axosoft-Reviews-E794943.htm', 'https://www.glassdoor.com/Reviews/Redfin-Reviews-E150726.htm', \
     'https://www.glassdoor.com/Reviews/Harsco-Reviews-E318.htm']


def test_page(css_selector, page=""):
    """Tests whether or not it took to long to access page
        css_selector = css selector that the driver should wait to appear.
        If the css_selector doesn't appear for 20 seconds it exits
    """
    if:
        # https://www.guru99.com/locators-in-selenium-ide.html
        WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR,css_selector )))
    except Exception as e:
        print("Took Long to access page " + page + "\n CSS Selector could be outdated ") # does not move to next phase of scraping!
        print(e)


def startDriverHeadless():
    """ sets and returns headless selenium driver
    """
    options = Options()
    options.headless = True
    driver = Chrome("/opt/WebDriver/bin/chromedriver", options=options)


def signinGlassdoor():
    """ Signs into glassdoor
        you can submit a username, password, and login url
    """
    USERNAME = config.gld_usr
    PASSWORD = config.gld_pwd
    login_url = "https://www.glassdoor.com/profile/login_input.htm"
    driver.get(login_url)
    
    driver.find_element_by_name("username").send_keys(USERNAME)
    driver.find_element_by_name("password").send_keys(PASSWORD)
    driver.find_element_by_xpath("//button[@class='gd-ui-button minWidthBtn css-1sdotxz' and @type='submit']").click()
    
    try:    
        test_page("div#Discover", login_url)
    except:
        print( "Signing into glassdoor failed. Please check credentials")
    
def remove_continue_reading():
    # click on all the continue readings for advice to management
    continue_readings = driver.find_elements_by_xpath("//div[@class='v2__EIReviewDetailsV2__continueReading v2__EIReviewDetailsV2__clickable']")
    count = 0
    attempts = 0
    
    while (len(continue_readings) > count) or attempts < 2:
        try:
            continue_readings[count].click()
            count += 1
        except:
            attempts += 1
            continue_readings = driver.find_elements_by_xpath("//div[@class='v2__EIReviewDetailsV2__continueReading v2__EIReviewDetailsV2__clickable']")        

def open_company_page(review_page):
    """ opens glassdoor company review page
    """
    urlToTest = "https://www.glassdoor.com/Reviews/" + review_page + ".htm?sort.sortType=RD&sort.ascending=false"

    driver.get( urlToTest )
    
    test_page("div#EIReviews", review_page)

def soup_it():
    """gets the HTML of the page the driver is on
    parses it with BeautifulSoup for navigation
    """ 
    # need to use the driver to interpret javascript as HTML
    reviewsHTML = driver.page_source
    soup = BeautifulSoup(reviewsHTML, 'lxml')
    return soup

def parse_datetime( dt ):
    """ Given glassdoor's review's date and time of being posted,
        parses the review into a datetime object
    """
    if dt != None:
        try: 
            gmt_offset = dt.partition('-')[2][1]

            dt2 = re.sub(r'\sGMT\-0[0-9]0{2}\s\(Pacific\s(Daylight|Standard)\sTime\)$', "", dt)

            return datetime.strptime(dt2, '%a %b %d %Y %H:%M:%S') - timedelta(hours = int(gmt_offset))
        except:
            print(dt)
    return None

def scrape_page( s, company_name, before = None, after = None):
    """ Input: Str of page source from a browser driver that captures the HTML of a page
                Name of company being scraped
                before, after: datetime.datetime objects describing range of dates that reviews scrapped should fall between
        Ouput: A list of list of reviews
        Scrapes all the reviews on the page. Each review is an array 
        Ultimately appends to an array that is passed into the function
        or creates a new array which it appends reviews to
    """
    
    
    def scrape_time(rev, before, after):
        """ 
            Input: bs4.element.Tag
            Returns datetime.datetime: The date and time of the review
            Returns None attribute used to scrape date and time doesn't have any text, or isn't found
        """
        times =  rev.find('time', attrs={'class': 'date subtle small'})
        if times != None:
            date_of_rev = parse_datetime(times['datetime'])
            if ( after != None ):
                if date_of_rev < after:
                    print(str(date_of_rev) + " < " + after + " so terminating loop")
                    return "break loop"
                else: 
                    if before != None:
                        if date_of_review > before:
                            return "next page"
                        else:
                            return date_of_rev
                    else:
                        return date_of_rev
            else:
                return date_of_rev
        else: 
            print("time was none")
            return None
    
    def scrape_title(rev):
        """ Input: bs4.element.Tag
            Returns str : title of the review
            Returns None attribute used to scrape title doesn't have any text, or isn't found in review
        """
        reviewTitle = rev.find('a', attrs={'class': 'reviewLink'} )
        if reviewTitle != None:
            return reviewTitle.get_text()[1:(len(reviewTitle.get_text())-1)]
        else:
            return None
        
    def scrape_rating(rev):
        """ Input: bs4.element.Tag
            Returns float : Overall rating of company by reviewer
            Returns None attribute used to scrape rating doesn't have any text, or isn't found in review
        """
        stars = rev.find( 'span', attrs={'class': 'rating'}).find('span')
        if stars != None:
            return float(stars['title'])
    
    def scrape_occupation(rev):
        """ Input: bs4.element.Tag
            Returns str : Overall rating of company by reviewer
            Returns None attribute used to scrape occupation doesn't have any text, or isn't found in review
        """
        jobTitle = rev.find('span', attrs={'class': 'authorJobTitle middle'})
        if jobTitle != None:
            return jobTitle.get_text().lower()
        else:
            print("Job title was None")
            return None
    
    def scrape_location(rev):
        """ Input: bs4.element.Tag
             Returns str : Overall location of company by reviewer
            Returns None attribute used to scrape location doesn't have any text, or isn't found in review
        """
        authorLoc = review.find('span', attrs={'class': 'authorLocation'})
        if authorLoc != None:
            return authorLoc.get_text()
        else:
            print("Author Location was none")
            return None
    
    def scrape_num_years(rev):
        """ Input: bs4.element.Tag
            Returns str: Overall str describing number of years reviewer worked at company
            Returns None attribute used to scrape number of reviews doesn't have any text, or isn't found in review
        """
        author_work_years = review.find('p', attrs={'class': 'mainText mb-0'} )
        if author_work_years != None:
            return author_work_years.get_text()
        else:
            return None
    def scrape_other_ratings(rev):
        """ Input: bs4.element.Tag
            Returns list of floats: Ratings of various aspects of the company:
                Work/Life Balance, Culture & Values, Career Opportunities, Compensation and Benefits, Senior Management
            Returns None attribute used to scrape number of reviews doesn't have any text, or isn't found in review
        """
        sub_ratings = []
        list_of_sub_ratings_to_parse = rev.find_all("span", attrs={'class': 'subRatings__SubRatingsStyles__gdBars gdBars gdRatings med'})
            
        if len(list_of_sub_ratings_to_parse) != 0:
            for sub_rating in list_of_sub_ratings_to_parse:
                sub_ratings.append( float(sub_rating['title']) if sub_rating != None else None )
                # if there aren't 5 ratings
            for i in range(0, 5-len(sub_ratings)):
                sub_ratings.append(None)
            return sub_ratings
        else:
            return [None]*5
        
    def scrape_pro_con_advice(rev):
        """ Input: bs4.element.Tag
            Returns list of strings/None: Corresponding the following reviewer's opinions on the company:
               Pros, Cons, Advice to Management
            Returns list of Nones: if attribute used to scrape number of reviews doesn't have any text, or isn't found in review
        """
        is_proconadvice = ['Pros', 'Cons', 'Advice to Management']
        counter = 0
        pro_con_advice_to_append = []
        
        prosconsadvice = rev.find_all('div', attrs={'class': 'v2__EIReviewDetailsV2__fullWidth'})
        
        for op in prosconsadvice:
            if op.find('p', attrs={'class': 'strong mb-0 mt-xsm'}) != None:
                op_type = op.find('p', attrs={'class': 'strong mb-0 mt-xsm'}).get_text()
                try:
                    while counter != is_proconadvice.index(op_type):
                        pro_con_advice_to_append.append(None)
                        counter +=1
                    
                    # find actual text of pro, con or advice
                    op_text = op.find('p', attrs={'class': 'mt-0 mb-xsm v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isExpanded'})
                    
                    if op_text != None:
                        pro_con_advice_to_append.append( op_text.get_text() )
                    else:
                        pro_con_advice_to_append.append( None )
                        
                    counter += 1
                except Exception as e:
                    """ This function relies on each header being in 'Pros', 'Cons', 'Advice to Management'
                    Something changed on glassdoor's site - either the headers or the attributes that reference the headers
                    """
                    print(e)
                    #pro_con_advice_to_append.append(None)
                    #counter+=1
            else:
                pro_con_advice_to_append.append(None)  
                counter+=1
        # Not every review has all three, or even any of the Pros, Cons and Advice
        # Section filled in. The counter appends Nones for unfilled sections
        while ( counter < 3 ):
            pro_con_advice_to_append.append( None )
            counter+=1
            
        return pro_con_advice_to_append
    
    ### Starts scraping input HTML source str here
    soup = BeautifulSoup(s, 'lxml')
    
    
    
    reviews = soup.find_all( 'div', attrs={'class': 'gdReview'})
    if len(reviews) == 0:
        print("No reviews on page!")
        return []
    
    # Will be an array of all reviews on the page
    output = []
    
    # Iterates over each review, and collects various aspects of the review
    for review in reviews:
        # Check if reivew is past 
        
        rw = []
        
        rw.append( company_name.split('-')[0] )
        
        # Check if the time of the review being scrapped falls out of the bounds of the before and after range
        #break the loop and stop scraping after this review and after
        date_of_review = scrape_time(review, before, after)
        if date_of_review == "break loop":
            break 
        elif date_of_review == "next page":
             continue
        else:
            rw.append( date_of_review )
        
        rw.append( scrape_title(review))
        rw.append( scrape_rating(review) )
        rw += scrape_other_ratings(review)
        rw.append( scrape_occupation(review) )
        rw.append( scrape_location(review) )
        rw.append( scrape_num_years(review) )
        rw += scrape_pro_con_advice(review)
        
        # append information scrapped from the review to array
        output.append(rw)
        
    if (len(output) == 0) and (date_of_review > before):
        return "next page"
    
    return(output)


def scrape_company( company_review_url):

    # https://www.glassdoor.com/Reviews/Axosoft-Reviews-E794943.htm
    company_page = company_review_url.split("/")[4].split(".")[0]

    # open browser using headless chrome driver
    options = Options()
    options.headless = True
    driver = Chrome("chromedriver.exe", options=options)

    # uses above driver to sign in
    signinGlassdoor()

    page_number = 1
    open_company_page(company_page)

    # sort the page by date, desc
    try: #li class="empReview cf"
        driver.find_element_by_xpath("//div[@class='gdReview']").click()
    except Exception as e:
        print(f"Issues could be \n. 1. URL is incorrect, check URL {URL}. \n. 2. Company doesn't have reviews \n 3. Glassdoor's website has changed significantly and this code needs to be updated. Check with admin".format(URL=company_page))
        print(e)
    count = 0
    # wait for page to load
    WebDriverWait(driver, 10)
    
    remove_continue_reading()
    
    # dataframe structure
    reviews = []
    reviews_df_colnames = [ 'company', 'date', 'title', 'company_stars', 'work_life_stars', 'culture_values_stars', 'career_ops_rating', "comp_bene_rating", "senior_manage_rating", 'author_employee_title', 'author_location', 'author_work_years', 'pros', 'cons', 'advice']

    company_df = []
    while True: 
        reviewsHTML = driver.page_source
        reviews_page_scraped = scrape_page( reviewsHTML, company_page, before = None, after = None )
        
        # if we're on the last page, or we have reached reviews that are past the before date
            
        if len(reviews_page_scraped) == 0:
            break

        page_number += 1
        count +=1
        
        # Go to next page, if function returns a
        if reviews_page_scraped == "next page":
            continue    

        company_df = company_df +  reviews_page_scraped

        # if the first page has passed, I want to check that the columns look correct
        if page_number == 1:
            data_quality_results = data_quality_check(pd.DataFrame(company_df, columns=reviews_df_colnames))
            if len(data_quality_results) != 0:
                raise ValueError("Some important columns are all null. Glassdoor HTML may have changed for data associated with these cols: " + data_quality_results)
            

        open_company_page(company_page + "_P" + str(page_number))
        
    driver.close()

    return pd.DataFrame(company_df, columns=reviews_df_colnames)


def data_quality_check( df ):
    """Input: dataframe
        Output: checks whether columns of dataframe have all nulls, or not
    """
    # cols to check for all nulls, update as needed
    output = df[cols_to_check].isna().sum() == df.shape[0]
    output = output.reset_index(drop = False)
    output = output.loc[ output[0] == False ,  ]['index'].tolist()

    return output
    

for company_review_url in company_review_urls:
    scrape_company(company_review_url)