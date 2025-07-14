from agents import Agent, RunContextWrapper, Runner, function_tool, set_default_openai_key
from searchTools import search_by_category, search_by_id, fuzzy_search
from ragAgent import vector_store_retriever_agent
from utils import get_user_info
import pydantic
import utils
from cartAgent import get_user_agent

async def get_agent_response(user_name, user_age, user_input, last_response_id=None, user_jwt=None, use_structuring=False):
    set_default_openai_key(utils.get_key())
    user = utils.User(name=user_name, 
                      age=user_age, 
                      last_response_id=last_response_id, 
                      user_jwt=user_jwt
                    )
    print(f"User Info: {user.name}, Age: {user.age}, JWT: {user.user_jwt}, Last Response ID: {user.last_response_id}")

    cart_manager = get_user_agent()
    inst =  """
                You are a shopping assistant for wallmart. You help users with all there needs with all the capabilities you have. 
                You are helpful assistant as well as a good salesman and you are to sell the products offered by the company that you can access
                through all the tools at your disposal. If the response has products you must include there product ids.
            """
    if not use_structuring: inst += "and you have to insert the product ids (int) in an xml tag <id></id>."

    agent = Agent[utils.User](name="Shopping Assistant",
                            instructions=inst,
                            model="gpt-4.1",
                            tools=[search_by_category,search_by_id,fuzzy_search,vector_store_retriever_agent],
                            handoffs=cart_manager
                            )
    
    try:
        result = await Runner.run(agent, user_input, previous_response_id=last_response_id, context=user)
    except Exception as e:
        raise ValueError(f"Error during Main agent run: {e}")
    final_output = result.final_output

    try:
        if use_structuring:
            final_output = utils.final_product_structured(final_output)
    except Exception as e:
        raise ValueError(f"Error in structuring final output: {e}")
    new_message_id = result.last_response_id
    
    return {
            "new_message_id": new_message_id, 
            "user_input": user_input,
            "final_output": final_output
            }