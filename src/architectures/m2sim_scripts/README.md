## copetest.py 

Usage: Run your executable -[flags + arguments] ELF_file [program arguments]"

  	 For example: python3 ./copetest.py -a x86 -s setting-2,setting-1 blocking 15

	 If you have a program and you would like it to be compiled here, use the -c flag and pass in the program file.
	 For example: python3 ./copetest.py -s setting-2 -c C++ blocking.cc 15

	 {os.path.basename(sys.argv[0])} Flags:

    -a      ARCHITECTURE    Architecture setting: x86, si, arm
    -c      COMPILE         Compile to ELF from a language other than C. Only supported language: C, C++ or Cpp, java
    -p      PATH            Path to m2s command
    -s      SETTING         Name of setting(s) directory, comma delimited & no space
    
Even with the compile flag, an executable or file name must be provided, and it must match the name of the executable the compiler builds

**This file is under the assumption that the user has Multi2Sim installed and its working**

- This file will run multi2sim on all available architectures unless a specific one is given.

- The multi2sim output will be pipelined to output file "m2sim_output_{arch}.output" and place it into the configured {settings} directory given: for example --> setting-1/m2sim_output_x86.output


