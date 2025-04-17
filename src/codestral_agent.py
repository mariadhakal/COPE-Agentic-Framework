import os
import json
from mistralai import Mistral, AssistantMessage, ToolMessage, UserMessage, SystemMessage
from mistralai.models.function import Function

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "Codestral-2501"


# Define a function that returns flight
# information between two cities (mock implementation)
def get_flight_info(origin_city: str, destination_city: str):
    if origin_city == "Seattle" and destination_city == "Miami":
        return json.dumps({
            "airline": "Delta",
            "flight_number": "DL123",
            "flight_date": "May 7th, 2024",
            "flight_time": "10:00AM"})
    return json.dumps({"error": "No flights found between the cities"})


# Define a function tool that the model
# can ask to invoke in order to retrieve flight information
tool = {
    "type": "function",
    "function": Function(
        name="get_flight_info",
        description="""Returns information about the next flight
            between two cities.
            This includes the name of the airline,
            flight number and the date and time
            of the next flight""",
        parameters={
            "type": "object",
            "properties": {
                "origin_city": {
                    "type": "string",
                    "description": ("The name of the city"
                                    " where the flight originates"),
                },
                "destination_city": {
                    "type": "string",
                    "description": "The flight destination city",
                },
            },
            "required": [
                "origin_city",
                "destination_city"
            ],
        }
    )
}


client = Mistral(api_key=token, server_url=endpoint)

messages = [
    SystemMessage(
        content="You are an assistant that helps users find flight information."),
    UserMessage(
        content=("I'm interested in going to Miami. What is "
                 "the next flight there from Seattle?")),
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