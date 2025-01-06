from ghidra.program.model.symbol import RefType # type: ignore
from ghidra.app.decompiler import DecompInterface # type: ignore
from ghidra.util.task import ConsoleTaskMonitor # type: ignore


def is_standard_library_function(function_name):
    """Check if the function is a standard library function."""
    # List of standard library functions to ignore in the final output
    stdlib_functions = {"printf", "scanf", "putchar", "exit", "malloc", "free", "puts", "__main"} 
    return function_name in stdlib_functions

decompinterface = DecompInterface()
decompinterface.openProgram(currentProgram) # type: ignore

# Get the main function
function_manager = currentProgram.getFunctionManager() # type: ignore
main_function = None

for func in function_manager.getFunctions(True):
    if func.getName() == "main":
        main_function = func
        break

if main_function:
    # Decompile the main function and get its code as a string
    decompiled_main = decompinterface.decompileFunction(main_function, 0, ConsoleTaskMonitor())
    if not decompiled_main.decompileCompleted():
        print("Error: Failed to decompile main!")
        exit()

    main_function_code = decompiled_main.getDecompiledFunction().getC()
    all_functions = list(function_manager.getFunctions(True)) 

    # Collect all relevant functions based on their names appearing in main
    relevant_functions = set([main_function])
    for func in all_functions:
        func_name = func.getName()

        if is_standard_library_function(func_name) or func in relevant_functions:
            continue

        # Check if the function name is in the main function code
        if func_name in main_function_code:
            relevant_functions.add(func)

    # Save decompiled relevant functions to a file
    with open("decompiled_output.c", "w") as output_file:
        for func in relevant_functions:
            decompiled_func = decompinterface.decompileFunction(func, 0, ConsoleTaskMonitor())
            if decompiled_func.decompileCompleted():
                output_file.write("// Function: {}\n".format(func.getName()))
                output_file.write(decompiled_func.getDecompiledFunction().getC())
                output_file.write("\n\n")
            else:
                output_file.write("// Failed to decompile function: {}\n".format(func.getName()))
                output_file.write("\n")

    print("Decompiled functions relevant to main saved to decompiled_output.c")
else:
    print("Error: 'main' function not found!")
