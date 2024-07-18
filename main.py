import json
import uvicorn
from typing import Optional
from models import Base, People
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import FastAPI, Depends, Form
from fastapi.middleware.cors import CORSMiddleware

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Allow all origins for CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency to get DB session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Root endpoint
@app.get('/')
async def home():
    return {"message": "Hello ByteGenine!"}

# Process endpoint to handle form data and perform SQL query
@app.post('/process')
async def process(prompt: Optional[str] = Form(None), db: Session = Depends(get_db)):
    try:
        # Get query from payload
        payload = json.loads(prompt)
        if "content" not in payload:
            raise Exception("Not valid query")
        
        # Perform SQL query
        result = db.execute(text("SELECT * FROM people WHERE first_name = :name"), {'name': payload["content"]})
        
        # Extract column names, drop id column
        columns = list(filter(lambda x: x != 'id', [col[0] for col in result.cursor.description]))

        # Convert result to list of dictionaries
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

        if len(rows) == 0:
            return {"columns": [], "rows": []}
        
        return {
            "columns": columns,
            "rows": rows
        }
    except Exception as e:
        return {"error": str(e)}

# Endpoint to get users by first name
@app.get("/people/{text}")
async def get_users(text, db: Session = Depends(get_db)):
    users = db.query(People).filter(People.first_name == text).first()
    return users

# Function to parse environment file for host and port
def parse_env_file():
    # Default host address and port number
    host = '0.0.0.0'
    port = 8080

    # Update from environment file if possible
    for file_name in [".env", ".env.local"]:
        try:
            with open(f'../BGTest_UI/{file_name}') as f:
                lines = f.readlines()
                host = lines[0].split('=')[1].strip()
                port = int(lines[1].split('=')[1].strip())
                break
        except Exception as e:
            print(f"Error occurred while loading from {file_name}")
            continue
    
    return host, port

if __name__ == "__main__":
    # Load host and port from env file
    host_name, port_num = parse_env_file()
    uvicorn.run("main:app", host=host_name, port=port_num)
