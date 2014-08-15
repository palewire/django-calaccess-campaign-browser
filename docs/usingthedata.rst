Data from Calaccess is dividing into major categories. This repository contains records about campaign finance data. For lobbying data, you will want to go to the lobbying data category. [lobbying data](https://github.com/california-civic-data-coalition/django-calaccess-lobbying-activity)

You can explore the data here, or you can also download the entire data-set or slices of it. But first, be aware of some critical caveats. 
--Allow time for the data updates: don't download until day after the deadline.  
--Note that non-ascii characters (á, é, í, ó, ú, ü, ñ, ¿, ¡) have all been converted to a, e, n, etc.  
--Donor address information is spotty but zipcode and city are generally filled out and can be useful for aggregation.    
--Contributor name has a last name field and a first name field. The last name is the only field that is filled in for corporations. Both fields are filled in for individuals.  
--If you are getting all the data, when analzying, remember that from the summary table, check itemized amounts against contributions (they should match).  
--Don't use detailed expenditure tables to run summary queries because credit card payments could be double-counted. The detailed credit card payment does include memo fields which can be informative, however.  

--Committees can campaign for more than one thing, and all the money is available to all of the things they support. So for example, if analyzing money on a specific proposition, you can only point out money available to be spent, not money actually spent for a particular proposition. 
 
--Totals and how to count late filings vs late filings:  
    You should wait for quarterly filings to actually total up contributions and you shouldn't mix quarterly filings       with late filings becasue late filings are only contributions over a certain dollar amount.  
--If you do pull down data, here are some basic queries that could be useful.  
   List of candidates with total contributions  
   Summary of contributions to candidate  
--Occupation field is often not filled in.  
Summary of contributions to committee      
Summary of contributions by the contributor  
Summary of contributions to candidate by campaign/race  
List of committees supporting/opposing an issue  
  
A few other sample questions: How much of the variation in election results are explained by contributions or expenditures  
    -For each candidate, how much they got or spent?  
    -How much did each vote cost?  
    -For each candidate, how many votes they got or how much they won/lost by.  

