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
- First tried ChatGPI model from OpenAI. It required secret key and has quota limitation.
- To avoid above limitation, decided to use open LLM model.
- Have some troubles to load pre-trained LLM model, as I have no GPU and not enough RAM memory.

### Things to improve
- Fine-tune the pre-trained LLM model with our custom data to improve NL->SQL conversion quality.