Data from Calaccess is dividing into major categories. This repository contains records about campaign finance data. For lobbying data, you will want to go to the lobbying data category. [lobbying data](https://github.com/california-civic-data-coalition/django-calaccess-lobbying-activity)


Contributions table queries
List of candidates with total contributions (sortable/searchable)
    filter
Summary of contributions to candidate
    filer
    committee
    total amount
    top contributions/contributors
List of contributions to candidate
    filer name
    filer address info (all fields)
    donor fname
    donor lname
    donor address info (city and zip are usually all that's there, but good to include rest where possible)
    contribution amount
    contribution date
    contribution election cycle
    contribution issue/race **see TODOs
    filter by:
        zip
        city
        contributor name (split first and last)
        date range
        election cycle
        issue/race
        
    other features:
        ability to choose which name variations to include    
    
Summary of contributions to committee    
Summary of contributions by the contributor
Summary of contributions to candidate by campaign/race (****needs to be added to parser - statement of organizations)
List of committees supporting/opposing an issue
Company summary across fields (use raw org name)
TODO: From summary table, check itemized amounts against contributions (they should match)
TODO: Need to add statement of organizations to parser
Expenditures table queries
List of candidates/committees with total expenditures (sortable/searchable)
    filter
Summary of candidate/committee expenditures
    filer
    committee
    total amount
    top contributions/contributors
List of candidate/committee expenditures
    filer name
    filer address info (all fields)
    recipient fname
    recipient address info (city and zip are usually all that's there, but good to include rest where possible)
    expenditure amount
    expenditure date
    explanation code
    explanation description
    transaction ID/back transaction id
    expenditure election cycle
    filter by:
        zip
        city
        payee name
        date range
        election cycle
        
    other features:
        filter out/in credit card payments from summary expenditures but keep memos
        ability to choose which name variations to include    
    
Summary of contributions to committee    
Summary of contributions by the contributor
Summary of contributions to candidate by campaign/race (****needs to be added to parser - statement of organizations)
List of committees supporting/opposing an issue
Company summary across fields (use raw org name)
TODO: join of expenditure codes
Fields/features
fuzzy name search
both ends of transaction
ability to add/subtract name variations from totals
filter in/out quarterly vs. late filings
filter by date:
    by election cycle
    by individual date/date range
    
filter by type of race (house, senate, other)
Dos and don'ts
committees can campaign for more than one thing, and all the money is available to all of the things they support
can only do money available, but not spent
Quarterly filings vs late filings
late filings are only contributions over a certain dollar amount
have to wait for quarterly filings to actually total up
don't mix quarterlies with late
don't download data until day after deadline (also need to factor in lag of parser in that case)
itemized vs unitemized?
have to use summary tables for totals, 
Note that non-ascii characters (á, é, í, ó, ú, ü, ñ, ¿, ¡) have all been converted to a, e, n, etc. (Is this the right way?)
expenditures: Don't confuse credit card bill for itemized expenditures
How should candidate vote total information tie in
Sample question: How much of the variation in election results are explained by contributions or expenditures
    -For each candidate, how much they got or spent
    -How much did each vote cost?
    -For each candidate, how many votes they got or how much they won/lost by
