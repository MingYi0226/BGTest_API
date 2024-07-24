# Introduction
This repository is FastAPI based backend for ByteGenie test project. It provides endpoints for ReactJS frontend.



# How to Run
- Install python dependencies from requirements.txt
  - pip install -r requirements.txt
- Run main.py
  - python main.py

# Notes
### Main steps and motiaton for data engineering/processing on the raw data 


### The main functionalities of the API
- /process(POST) 
    - Parse the API request payload
    - Returns if 'content' field(natural language query) is not exist
    - Feed the query into model and get the output(SQL query).
    - Execute the SQL query
    - Returns column names and list of rows if valid data fetched.
    - Returns two empty lists for empty result.
- /(GET)
    - Returns {"message": "Hello ByteGenine!"}
### Key challenges I faced
- Wondered which method to use for natural language query into SQL query.
- First I tried to use HuggingFace model to convert user's natural query into SQL statements directly without modifying database schema. But due to lack of RAM size of my PC and no GPU acceleration, running such huge model was impossible.
- So switched to OpenAI model. It's speed is fast but probably we will suffer token limitation when we deploy this backend server.

### Things to improve
- Replace OpenAI GPT model which is online with SQLCoder model in local, so does not depend on token limitation.(sqlcoder_test.py)
- Fine-tune the pre-trained LLM model with our custom data to improve NL->SQL conversion quality.

### Sample answers
You can get following result with openai_test.py
  1. Find me companies that are attending Oil & Gas related events over the next 12 months
  ```sql
SELECT *
FROM company
WHERE event_url IN
    (SELECT event_url
     FROM event
     WHERE event_industry LIKE '%oil & gas%')
  AND event_start_date BETWEEN date('now') AND date('now', '+1 year')
  ```
  Answer: No results or an error occurred.

  2. Find sales people for companies that are attending events in Singapore over the next 9 months.
  ```sql
  SELECT DISTINCT p.first_name,
                p.last_name,
                p.job_title,
                c.company_name
FROM people p
JOIN company c ON c.homepage_base_url = p.homepage_base_url
JOIN event e ON e.event_url = c.event_url
WHERE e.event_country LIKE '%Singapore%'
  AND e.event_start_date >= '2024-07-25'
  AND e.event_start_date <= '2025-04-25'
  ```
  Answer: Query Fetched 1473 rows:

  3. Find me events that companies in Pharmaceuticals sector are attending.
  ```sql
  SELECT event.event_name
FROM event
JOIN company ON event.event_url = company.event_url
WHERE company.company_industry LIKE '%pharmaceuticals%'
  ```
  Answer: No results or an error occurred.

  4. I need the email addresses of people working for companies that are attending inance and banking events.
  ```sql
  SELECT DISTINCT p.email
FROM people p
JOIN company c ON p.homepage_base_url = c.homepage_base_url
JOIN event e ON c.event_url = e.event_url
WHERE e.event_industry like '%finance%'
  OR e.event_industry like '%banking%'
  ```
  Answer: Query Fetched 155 rows: