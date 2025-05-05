import os
import json
from mistralai import Mistral, AssistantMessage, ToolMessage, UserMessage, SystemMessage
from mistralai.models.function import Function
import re
from java_code_parser import java_parser
import javalang

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "Codestral-2501"

# Initialize model
client = Mistral(api_key=token, server_url=endpoint)


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
    You're a Java code parsing assistant. Your task is to analyze Java code provided by users.

    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    
    Use Thought to describe why you’re doing what you’re doing.
    Use Action to invoke one of your tools, then return PAUSE.
    Observation will be filled in with the result of that action.
    
    Your available tools are: 
    • java_code_parser:  
        - Input: a Java code snippet (method or class)
        - Behavior: parses the Java code and produces an abstract syntax tree (AST)
        - Example:  
            Action: java_code_parser: public class Operations{public int fib(int n) { return n < 2 ? n : fib(n-1)+fib(n-2); }}

When given Java code:
1. First, check if the code appears to be valid Java syntax (proper brackets, semicolons, etc.)
2. Assess if the code is a complete method, class, or if it needs to be wrapped
3. Use the java_code_parser tool to try parsing the code
4. Analyze the parser response:
   - If successful, examine the AST structure
   - If unsuccessful, identify why the parsing failed and suggest corrections
5. Provide feedback on whether the code is in an acceptable format for javalang parser
6. Summarize your findings in the final Answer

Example session:

Question: Parse this Java code:
public int calculate(int x, int y) {
    return x + y;
}

Thought: I need to analyze this Java method that calculates the sum of two integers. I'll use the java_code_parser 
tool to get the AST.

Action: java_code_parser: public int calculate(int x, int y) { return x + y; }

PAUSE

Observation: {"methodName": "calculate", "returnType": "int", "parameters": [{"type": "int", "name": "x"}, 
{"type": "int", "name": "y"}], "body": {"type": "ReturnStatement", "expression": {"type": "BinaryOperation", 
"operator": "+", "leftOperand": "x", "rightOperand": "y"}}}

Thought: Now I can analyze the AST. This is a simple method that takes two integer parameters and returns their sum.

Answer: The code defines a method named 'calculate' that:
- Takes two integer parameters: x and y
- Returns an integer value
- Has a simple implementation that adds x and y and returns the result
- Has a time complexity of O(1) and space complexity of O(1)

""".strip()


def java_code_parser(snippet):
    """
    Wrapper function that calls the parse_java_code function from the imported module.
    This function will attempt to parse the Java code and return the AST.
    If parsing fails, it returns an error message.
    """
    is_full_cu = (
            snippet.lstrip().startswith(("package", "public class", "class"))
            or "interface" in snippet
            or "enum" in snippet
    )
    code = snippet if is_full_cu else f"class _Wrapper {{ {snippet} }}"
    try:
        # Call the parse_java_code function from your module
        return java_parser(code)
    except Exception as e:
        return f"Error parsing code: {str(e)}"


known_actions = {
    "java_code_parser": java_code_parser,
}

# Creating a loop for tool calling agent
action_re = re.compile(r'^\s*Action:\s*(\w+)\s*:\s*(.*)$')  # python regular expression to selection action


def query(code, max_turns=5):
    i = 0  # counter to keep track of iterations
    bot = Agent(prompt)  # initialize agent with default system prompt
    next_prompt = f"Parse and analyze this Java code:\n{code}\n"

    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)

        # actions = [
        #     action_re.match(a)
        #     for a in result.split("\n")  # parse the content of the result
        #     if action_re.match(a)
        # ]
        actions = [
            action_re.match(line.strip())
            for line in result.splitlines()
            if action_re.match(line.strip())
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

if __name__ == "__main__":
    sample_code = """
    public int setSecurityMode ( int level, String authToken ) throws RemoteException {
    if ( !this.authToken.equals( authToken )){
        throw new RemoteException( "Invalid Login Token" );
    }
    ServerSettingBean.setSecureMode( "" + level );
    serverSettingBean.updateSettings();
    securityMode = level;
    return securityMode;
}
    """

    query(sample_code)
    # print(analysis)
