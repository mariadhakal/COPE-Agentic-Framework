import json
import time
import sys
import os
import string
import random

# cope take program as input and feeds it to llm to process, 
# llm could theoretically call a tool to call multisim using the program input

def usage(status=0):
    print(f'''Usage: Run your executable -[flags + arguments] ELF_file [program arguments]"

  	 For example: python3 ./copetest.py -s setting-2 blocking 15

	 If you have a program and you would like it to be compiled here, use the -c flag and pass in the program file.
	 For example: python3 ./copetest.py -s setting-2 -c C++ blocking.cc 15

	 {os.path.basename(sys.argv[0])} Flags:

    -a      ARCHITECTURE    Architecture setting: x86, arm, cuda
    -c      COMPILE         Compile to ELF from a language other than C. Only supported language: C, C++ or Cpp, java
    -p      PATH            Path to m2s command
    -s      SETTING         Name of setting directory
    
	 Even with the compile flag, an executable or file name must be provided, and it must match the name of the executable the compiler builds''')
    sys.exit(status)

def parse_stats(sett, output, arch):

    with open(f"{output}", 'r') as fp:
        lines = fp.readlines()

    # Write file
    with open(f"{output}", 'w') as fp:
        for number, line in enumerate(lines):
            if number not in [0,1,2,3,4,5,6,8,9]:
                if number == 7:
                    fp.write(line[2:])
                else:
                    fp.write(line)
    return

def config_outputfile(sett, output, arch):

    # parse mem-config
    with open(f"{sett}/mem-config", 'r') as fp:
        mem_lines = fp.readlines()

    # parse arch-config
    with open(f"{sett}/{arch}-config", 'r') as fp:
        arch_lines = fp.readlines()

	 # add configurations to simulation output
    with open(f"{output}", 'a') as fp:
        fp.write("Architecture Configuration:\n") 
        for al in arch_lines:
            fp.write(al)
        fp.write("Memory Configuration:\n")
        for ml in mem_lines:
            fp.write(ml)
    return
 
def compile_cmd(lang, filename):
    executables = str(filename)
    executables = executables.split('.')
    executable = str(executables[0])

    if lang == 'C':
        cmpcmd =  f"gcc {filename} -std=gnu99 -m32 -Wall -g -o {executable}"
        os.system(cmpcmd)
    elif lang == 'C++' or lang == 'Cpp':
        cmpcmd =  f"g++ {filename} -m32 -O3 -o {executable}"
        os.system(cmpcmd)
    elif lang == 'java':
        cmpcmd = f""

    return executable


def main():
    # flags: 
    # default values
    compile_flag = False
    executable = None
    filename = None
    cmpcmd = None
    sett = 'setting-1'
    arch = 'x86'
    path = 'm2s'
    output = 'm2sim_output'

    arguments = sys.argv[1:]

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0) # detect flag and pop -

        if argument == '-a':
            arch = arguments.pop(0) # shift

        elif argument == '-c':
            compile_flag = True 
            lang = arguments.pop(0) # shift

        elif argument == '-p':
            path = arguments.pop(0) # shift
    
        elif argument == '-s':
            sett = arguments.pop(0) # shift
    
        elif argument == '-h':
            usage(0)

    if arguments:
        filename = arguments.pop(0)
    else:
        usage(1)

    if compile_flag:
        executable = compile_cmd(lang, filename)
    else:
        executable = filename

    # program running different settings too?, give filename id #

    # call m2sim < executable
    # run all three architectures
    if arch == '':
        archs = ['x86', 'arm']
        for i,a in enumerate(archs):
            arch = a
            of = f"{sett}/{output}_{a}.output"
            m2scmd = f"{path} --{arch}-sim detailed --{arch}-config {sett}/{arch}-config --mem-config {sett}/mem-config --{arch}-report {sett}/{arch}-out.txt --mem-report {sett}/mem-out.txt {executable} {' '.join(arguments)} 2> {of}"
            print(m2scmd)
            os.system(m2scmd)

            # Parse statistics summaryfiles
            parse_stats(sett,of,arch)

            # add config ot stats summary
            config_outputfile(sett,of,arch)

    else: # run 1 specified architecture
        print(arguments) 
        of = f"{sett}/{output}_{arch}.output"
        m2scmd = f"{path} --{arch}-sim detailed --{arch}-config {sett}/{arch}-config --mem-config {sett}/mem-config --{arch}-report {sett}/{arch}-out.txt --mem-report {sett}/mem-out.txt {executable} {' '.join(arguments)} 2> {of}"
        print(m2scmd)
        os.system(m2scmd)

        print("\nParse stats", of)
        # Parse statistics summary file
        parse_stats(sett,of,arch)

        print("Config files", of)
        # Add config to stats summary
        config_outputfile(sett,of,arch)

    return

if __name__ == "__main__":
    main()
