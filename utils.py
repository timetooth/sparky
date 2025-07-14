from agents import function_tool, RunContextWrapper
from openai import OpenAI, RateLimitError
import pydantic
import pymongo
import dotenv
import time
import json
import sys
import os
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class User(pydantic.BaseModel):
    name: str
    age: int
    last_response_id: Optional[str] = None
    user_jwt: Optional[str] = None


def get_key():
    dotenv.load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return openai_api_key
    else:
        raise ValueError("OpenAI API key not found in the environment variables.")

def get_node_base_uri():
    dotenv.load_dotenv()
    node_base_uri = os.getenv("NODE_BASE_URI")
    if node_base_uri:
        return node_base_uri
    else:
        raise ValueError("Node base URI not found in the environment variables.")

def write_out(output):
    res_path = os.path.join(BASE_DIR, 'res.txt')
    with open(res_path, 'w') as f:
        f.write(output)
    return

def write_out(output,fresh=False):
    mode = 'a'
    if fresh: mode = 'w'
    res_path = os.path.join(BASE_DIR, 'res.txt')
    with open(res_path, mode) as f:
        f.write("\n" + '*'*10+time.strftime("%Y/%m/%d, %H:%M:%S") + '*'*10 + "\n")
        f.write(output)
    return

def get_products_collection():
    uri = os.getenv('MONGO_URI')
    client = pymongo.MongoClient(uri)
    db = client.get_database("Spark")
    collection = db.get_collection("products")
    return collection

def initialize_openai_client():
    key = get_key()
    org_key = os.getenv('OPENAI_ORG_KEY')
    project_id = os.getenv('OPENAI_PROJECT_ID')

    client = OpenAI(
        api_key=key,
        organization=org_key,
        project=project_id,
    )
    return client

def get_embedding(text, model="text-embedding-3-large"):
    client = initialize_openai_client()
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

@function_tool
async def get_user_info(context: RunContextWrapper[User]) -> str:
    """
    Get user information. Specifically, the name and age of the user.
    """
    return f'{context.context.name} is {context.context.age} years old.'

@function_tool
def retrieve_products(query:str,limit:int) -> str:
    query_embedding = get_embedding(query)
    collection = get_products_collection()
    pipeline = [
    {
        "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "exact": True,
                "limit": limit
        }
    }, 
    {
        "$project": {
            "_id": 1,
            "embedding_text": 1,
            "score": {
                "$meta": "vectorSearchScore"
            }
        }
    }
    ]
    results = collection.aggregate(pipeline)
    text = "Here are All the Products Fetched from the vector Database:\n"
    for result in results: text += f"\nID: {result['_id']}, \nProduct: {result['embedding_text']}, \nMatch score: {result['score']}\n"
    return text

def final_product_structured(agent_response: str, model="gpt-4o") -> str:
    client = initialize_openai_client()
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "system", 
                    "content":  """
                                    You Structure outputs for an ai shopping assistant.
                                    You will be given proper markdown response.
                                    The response should remain exactly same.
                                    If there are products, you have to insert the product ids in an xml tag <id></id>.
                                    Do this only for the products with ids.
                                """
                },
                {
                    "role": "user",
                    "content": agent_response,
                },
            ]
        )
    except RateLimitError:
        return final_product_structured(agent_response, model="gpt-4")
    return response.output_text

