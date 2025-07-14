from agents import Agent, RunContextWrapper, Runner, function_tool, set_default_openai_key
from cartTools import add_item_to_cart, get_all_items_in_cart, remove_all_items, remove_item_from_cart
from searchTools import search_by_id, fuzzy_search
import pydantic
import utils
import asyncio

def get_user_agent():
    agent = Agent[utils.User](
        name="Cart Manager",
        instructions="""You are the cart Manager for Walmart application.
        You help users with managing their cart using the all the tools at your desposal.
        You help people with managing their cart. You can add items to the cart, remove items from the cart, and view the cart contents and clear all items in the cart.
        If there is any confusion about the product, you can search for the product using the search by id tool or the fuzzy search tool and hence execute the rest of the task.
        If there are any products in your response, you must have product ids and you have to insert the product ids (int) in an xml tag <id></id>..
        """,
        model="gpt-4.1",
        tools=[search_by_id, fuzzy_search, add_item_to_cart, get_all_items_in_cart, remove_all_items, remove_item_from_cart],
        handoff_description="""
            This is a cart manager for Walmart application, with capabilities to:
            - search for specific product
            - add items to the cart
            - remove items from the cart 
            - view the cart contents
            - clear all items in the cart
        """,
    )
    return agent