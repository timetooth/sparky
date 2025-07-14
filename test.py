from agents import Agent, RunContextWrapper, Runner, function_tool, set_default_openai_key, handoff
import utils
from pydantic import BaseModel

class additional_info(BaseModel):
    user_nick_name: str
    user_email: str

@function_tool
def get_user_info(context_wrapper: RunContextWrapper[utils.User]) -> str:
    """
    Get user information. Specifically, the name and age of the user.
    """
    print("-------------- get_user_info called --------------")
    user = context_wrapper.context
    print(f"User Info: {user.name}, Age: {user.age}")
    print("-------------- get_user_info ended --------------")
    return f'{user.name} is {user.age} years old.'

test = Agent[utils.User](
    name="Test Agent",
    instructions="You are a test agent you have to call the get_user_info tool no matter what and return the raw response",
    model="gpt-4.1",
    tools=[get_user_info],
    handoff_description="""This is a test agent. you must call this"""
)

main = Agent[utils.User](
    name="Hand off agent",
    instructions="You are a hand off agent. handoff to test agent no matter what",
    model="gpt-4.1",
    handoffs=[test]
)

user = utils.User(name="casterly",age=30)
more_user = additional_info(user_nick_name="keys", user_email="cast@gmail.com")

res = Runner.run_sync(main, "Do what instructions say", context=user)

print(res.final_output)