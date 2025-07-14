from agents import Agent, RunContextWrapper, Runner, function_tool, set_default_openai_key
import pydantic
import utils
import asyncio

@function_tool
async def vector_store_retriever_agent(context_wrapper: RunContextWrapper[utils.User], query: str) -> str:
    """
    Retrieve relevant Products,this tool accepts a raw user query. 
    The RAG agent mixes this with context itself and uses it to create an embedding and search the vector database for relevant products.
    returns very products with very specific details. Use this especially when the user query is very specific and you have enough context
    to retrieve products that match the query better.

    Args:
        query (str): The complete raw user query string

    Returns:
        str: Details of Products Fetched along with product ids.
    """
    last_response_id = context_wrapper.context.last_response_id

    agent = Agent(
            name="rag_agent",
            instructions="""
                        You are a Vector Store Retrieval Agent. 
                        You will be given a raw user querry and you have to build a full querry with conversation context and the user query. 
                        Your job is to retrieve and filter relevant products from the vector store effectively.
                        The Output should be strictly from the retrived products and you must strictly include retrieved product ids and all product details in your response.
            """,
            model="gpt-4.1",
            tools=[utils.retrieve_products],

    )

    result = await Runner.run(agent, query, previous_response_id=last_response_id)

    return result.final_output