import os
import json
from mistralai import Mistral, AssistantMessage, ToolMessage, UserMessage, SystemMessage
from mistralai.models.function import Function
import re

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "Codestral-2501"

# Initialize model
client = Mistral(api_key=token, server_url=endpoint)

# Write the prompt
user_message = """
    Evaluate the performance of this java code:
"""

messages = [
    SystemMessage(
        content="You are an assistant that helps users to evaluate the performance of java code."),
    UserMessage(
        content=f"{user_message}"),
]

# Call the llm
response = client.chat.complete(
    messages=[{"role": "user", "content": "Hello world"}],
    model=model_name,
)


# print(response.choices[0].message.content)

class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    # What we want agent to do?
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        response = client.chat.complete(
            messages=self.messages,
            model=model_name,
        )
        return response.choices[0].message.content


prompt = """
    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    Use Thought to describe your thoughts about the question you have been asked.
    Use Action to run one of the actions available to you - then return PAUSE.
    Observation will be the result of running those actions.
    
    Your available actions are:
    java_code_parser:
    e.g. java_code_parser: 4 * 7 / 3
    Runs a java parser and returns the abstract syntax tree - uses javalang to parse the code so be sure the code being entered is in java language
    
    dynamic_profiling:
    e.g. dynamic_profiling: jvm
    returns execution time of the java code
    
    Example session:
    
    Question: How much does a Bulldog weigh?
    Thought: I should look the dogs weight using average_dog_weight
    Action: average_dog_weight: Bulldog
    PAUSE
    
    You will be called again with this:
    
    Observation: A Bulldog weights 51 lbs
    
    You then output:
    
    Answer: A bulldog weights 51 lbs
""".strip()

def java_code_parser(what):
    return eval(what)

def dynamic_profiling(name):
    if name in "Scottish Terrier":
        return("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return("a toy poodles average weight is 7 lbs")
    else:
        return("An average dog weights 50 lbs")

known_actions = {
    "java_code_parser": java_code_parser,
    "dynamic_profiling": dynamic_profiling
}

# Creating a loop for tool calling agent
action_re = re.compile('^Action: (\w+): (.*)$')   # python regular expression to selection action

def query(question, max_turns=5):
    i = 0 # counter to keep track of iterations
    bot = Agent(prompt) # initialize agent with default system prompt
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_re.match(a)
            for a in result.split("\n") # parse the content of the result
            if action_re.match(a)
        ]

        if actions:
            # there is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print("-- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return


# Calling an agent

question = """I have 2 dogs, a border collie and a scottish terrier. \
What is their combined weight"""
query(question)
