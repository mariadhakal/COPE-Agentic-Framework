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

source_code = """public int setSecurityMode ( int level, String authToken ) throws RemoteException {
if(!this.authToken.equals( authToken )){
throw new RemoteException( "Invalid Login Token" );
}
ServerSettingBean.setSecureMode(""+level);
serverSettingBean.updateSettings();
securityMode = level;
return securityMode;
}"""
try:
    tree = javalang.parse.parse(source_code)
    print(tree.package.name)  # 'example'
    for type_decl in tree.types:
        print(type_decl.name)  # 'Test'
except javalang.parser.JavaSyntaxError as e:
    print("Syntax error:",e)
