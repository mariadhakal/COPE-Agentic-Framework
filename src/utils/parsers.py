# import subprocess
# import json
#
# def parse_code_with_javaparser(file_path: str) -> dict:
#     """
#     Call JavaParser via a subprocess to analyze the Java source file.
#     The JavaParser tool should output JSON to stdout.
#     """
#     try:
#         # Adjust the command as needed (e.g., path to your jar and any arguments)
#         result = subprocess.run(
#             ["java", "-jar", "path/to/javaparser-tool.jar", file_path],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         # Assuming the output is a JSON string with the callgraph and AST information.
#         parsed_output = json.loads(result.stdout)
#         return parsed_output
#     except subprocess.CalledProcessError as e:
#         # Handle errors as needed
#         print("Error calling JavaParser:", e)
#         return {}

import javalang

# source_code = """public class Wrapper {public int setSecurityMode(int level, String authToken) throws RemoteException {
#         if (!this.authToken.equals(authToken)) {
#             throw new RemoteException("Invalid Login Token");
#         }
#         ServerSettingBean.setSecureMode("" + level);
#         serverSettingBean.updateSettings();
#         securityMode = level;
#         return securityMode;
#     }}"""
source_code = """
public class HelloWorld{
	public static void main(String[] args) {
		System.out.println("Hello World!");
	}
}
"""


def print_ast(node, indent=0):
    # Print the node type and, if available, its name
    node_type = type(node).__name__
    name = getattr(node, 'name', None)
    print('  ' * indent + f'{node_type}' + (f': {name}' if name else ''))
    # Recursively print children
    if hasattr(node, 'children'):
        for child in node.children:
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, javalang.ast.Node):
                        print_ast(item, indent + 1)
            elif isinstance(child, javalang.ast.Node):
                print_ast(child, indent + 1)


try:
    tree = javalang.parse.parse(source_code)
    print_ast(tree)
except javalang.parser.JavaSyntaxError as e:
    print("Syntax error:", e)
