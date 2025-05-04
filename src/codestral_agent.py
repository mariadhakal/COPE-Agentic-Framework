import os
import json
from mistralai import Mistral, AssistantMessage, ToolMessage, UserMessage, SystemMessage
from mistralai.models.function import Function

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "Codestral-2501"

client = Mistral(api_key=token, server_url=endpoint)

user_message = """
    Evaluate the performance of ths java code......
"""

messages = [
    SystemMessage(
        content="You are an assistant that helps users to evaluate the performance of java code."),
    UserMessage(
        content=f"{user_message}"),
]

response = client.chat.complete(
    messages=messages,
    tools=[tool],
    model=model_name,
)

# We expect the model to ask for a tool call
if response.choices[0].finish_reason == "tool_calls":

    # Append the model response to the chat history
    messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))

    # We expect a single tool call
    if response.choices[0].message.tool_calls and len(
      response.choices[0].message.tool_calls) == 1:

        tool_call = response.choices[0].message.tool_calls[0]

        # We expect the tool to be a function call
        if tool_call.type == "function":

            # Parse the function call arguments and call the function
            function_args = json.loads(
                tool_call.function.arguments.replace("'", '"'))
            print(f"Calling function `{tool_call.function.name}` "
                  f"with arguments {function_args}")
            callable_func = locals()[tool_call.function.name]
            function_return = callable_func(**function_args)
            print(f"Function returned = {function_return}")

            # Append the function call result fo the chat history
            messages.append(
                ToolMessage(
                    name=tool_call.function.name,
                    content=function_return,
                    tool_call_id=tool_call.id,
                )
            )

            # Get another response from the model
            response = client.chat.complete(
                messages=messages,
                tools=[tool],
                model=model_name,
            )

            print(f"Model response = {response.choices[0].message.content}")