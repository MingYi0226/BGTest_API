import sqlparse
import json
import openai
import sqlite3

openai.api_key = 'sk-proj-xxxx'

table_metadata = """
You are a data analyst and interpreter. You will be given information about a specific dataset, including its columns and their meanings:
    people.first_name: This column is the first name of a person, example Cynthia
    people.middle_name: This column is the middle name of a person and can be empty.
    people.last_name: This column is the last name of a person, example Shanley
    people.job_title: Represents the job of the person, example Indirect Buyer
    people.person_city: Represents the city where the person lives.
    people.person_state: Represents the state of the person, example North Carolina, FL
    people.person_country: Country name of the person, example US, DE, Germany.
    person.email_pattern: Represents how the email looks like, example [first].[last], [first_initial].[last]
    person.email: Represents the email address of the person.
    person.homepage_base_url: Represents the hompage url.
    event.event_name: Represents the title of the event.
    event.event_start_date: Represents the start date of the event in year-month format, exmample 2024-07-06.
    event.event_end_date: Represents the end date of the event in year-month format, exmample 2024-07-06.
    event.venue: Represents the place where the event occurs, example Suntec Singapore, Best Western Plus Hotel & Conference Center.
    event.event_country: Represents the country where event occurs, example Singapore, Australia
    event.event_description: Represents the details of the event.
    event.event_url: Represents the url of the event.
    event.event_industry: Represents ths industry that event belongs to.
    company.company_revenue: Represents the profit of the company, example $355 million
    company.company_industry: Represents the industry that compay belongs to, similar as event.event_industry
    event.n_employees: Represents the total number of employees of the company, example 1,001-5,000, 104.0

    event.event_url=company.event_url.
    company.homepage_base_url=people.homepage_base_url

    If you cannot answer the question with the available database schema, return 'I do not know'
    Current date is 2024-07-25.
    Use like syntax for string compare in WHERE clause. For example event.event_industry = 'x' to event.event_industry like '%x%'

    Using this information, you will set up the most suitable SQLite statements to answer questions related to the data. These SQLite statements will later be executed, so they should be error-free, compatible with Sqllite syntax, and accurately respond to the questions asked. Do not express an opinion or try to explain. Return only the SQLite statement. Remember your sql statement will run on SQLite so syntax should be correct. 
    You MUST dont use DATEADD, ILIKE, and INTERVAL syntax. 
CREATE TABLE "people" (
	"first_name"    TEXT,
	"middle_name"   TEXT,
	"last_name"     TEXT,
	"job_title"     TEXT,
	"person_city"   TEXT,
	"person_state"  TEXT,
	"person_country"        TEXT,
	"email_pattern" TEXT,
	"homepage_base_url"     TEXT,
	"duration_in_current_job"       TEXT,
	"duration_in_current_company"   TEXT,
	"email"   TEXT
)
CREATE TABLE "event" (
	"event_logo_url"        TEXT,
	"event_name"    TEXT,
	"event_start_date"      TEXT,
	"event_end_date"        TEXT,
	"event_venue"   TEXT,
	"event_country" TEXT,
	"event_description"     TEXT,
	"event_url"     TEXT,
	"event_industry"   TEXT
)
CREATE TABLE "company" (
	"company_logo_url"      TEXT,
	"company_logo_text"     TEXT,
	"company_name"  TEXT,
	"relation_to_event"     TEXT,
	"event_url"     TEXT,
	"company_revenue"       TEXT,
	"n_employees"   TEXT,
	"company_phone" TEXT,
	"company_founding_year" TEXT,
	"company_address"       TEXT,
	"company_industry"      TEXT,
	"company_overview"      TEXT,
	"homepage_url"  TEXT,
	"linkedin_company_url"  TEXT,
	"homepage_base_url"     TEXT,
	"company_logo_url_on_event_page"        TEXT,
	"company_logo_match_flag"       TEXT
)

"""


def run_conversation(query):
    # Step 1: send the conversation and available functions to GPT

    prompt = f"""
{table_metadata}
Now please convert the query below into working SQLite and execute it:

{query}
    """
    messages = [{"role": "user", "content": prompt}]
    functions = [
        {
            "name": "sql_query",
            "description": "Execute the given SQL query and return the results",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_query": {
                        "type": "string",
                        "description": "The SQL query to execute",
                    }                },
                "required": ["target_query"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    # print(response["choices"][0])
    try:
        response_message = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])["target_query"]
        formatted_sql = sqlparse.format(response_message, reindent=True)
    except Exception as e:
        return ''
    return formatted_sql


def execute_sql_query(sql_query):
    connection = sqlite3.connect('..\BGTest_DB\Database.db')
    cursor = connection.cursor()

    try:
        # Execute the SQL query
        cursor.execute(sql_query)
        connection.commit()

        # Fetch all results (if the query returns any)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        # Close the connection
        connection.close()
        
if __name__ == '__main__':
    questions = [
        "Find me companies that are attending Oil & Gas related events over the next 12 months",
        "Find sales people for companies that are attending events in Singapore over the next 9 months.",
        "Find me events that companies in Pharmaceuticals sector are attending",
        "I need the email addresses of people working for companies that are attending finance and banking events."
	]
    for query in questions:
        res = run_conversation(query.lower())
        results = execute_sql_query(res)
        print(query, '\n', res)
        if results:
            print(f">> Query Fetched {len(results)} rows:")
        else:
            print(">> No results or an error occurred.")