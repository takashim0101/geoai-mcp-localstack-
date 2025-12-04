import pkgutil
import inspect
import sys

def find_function_in_modules(function_name):
    found_locations = []
    for importer, modname, ispkg in pkgutil.walk_packages(onerror=lambda n: None):
        if 'langchain' in modname:
            try:
                # Attempt to import the module
                module = __import__(modname, fromlist=['dummy'])
                # Check if the function_name is directly in the module's __dict__
                # or if it's a submodule that might contain it
                if hasattr(module, function_name):
                    found_locations.append(f"Found '{function_name}' in module: {modname}")
                # If it's a package, we might need to look deeper, but walk_packages handles this
            except Exception:
                # Ignore import errors for modules that might not be fully installed or have issues
                pass
    return found_locations

print("Searching for 'create_tool_calling_agent'...")
results_create_agent = find_function_in_modules('create_tool_calling_agent')
if results_create_agent:
    for r in results_create_agent:
        print(r)
else:
    print("Not found.")

print("\nSearching for 'AgentExecutor'...")
results_executor = find_function_in_modules('AgentExecutor')
if results_executor:
    for r in results_executor:
        print(r)
else:
    print("Not found.")

