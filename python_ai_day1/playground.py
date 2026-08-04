# forecast : list[float] = [22.5, 23.1, 21.8]      # list

# def main ()-> None:
#     city : str = "Tokyo"              # str
#     temperature : float = 22.5          # float

    

#     for day_temp in forecast:
#         if day_temp > 23:
#             print(f"{day_temp}°C — warm day")
#         else:
#             print(f"{day_temp}°C — mild day")
#     return f"{city} is currently {temperature}°C."


# if __name__ == "__main__":
#     print(main())
##################################################################


# def add_timing(func):  # This is a decorator
#     def wrapper(*args, **kwargs):
#         print(f"Calling {func.__name__}...")
#         result = func(*args, **kwargs)
#         print(f"Done! {func.__name__}")
#         return result
#     return wrapper

# @add_timing
# def greet(name):
#     return f"Hello, {name}!"

# print(greet("Alice"))

##################################################################
# What Does @functools.wraps(func) Do?
# Problem it solves: When you create a wrapper function inside a decorator, the wrapper function loses the original function's identity.

# Without @functools.wraps(func)
# The wrapper function replaced all the original greet function's metadata. This is bad because:

# Debugging tools get confused (they see "wrapper" instead of "greet")
# Help documentation disappears
# IDE autocompletion loses the docstring


# def my_decorator(func):
#     def wrapper(*args, **kwargs):
#         print("Before calling function")
#         return func(*args, **kwargs)
#     return wrapper

# @my_decorator
# def greet(name: str) -> str:
#     """Say hello to someone."""
#     return f"Hello, {name}!"

# print(greet.__name__)      # Output: wrapper  ❌ WRONG! Should be 'greet'
# print(greet.__doc__)       # Output: None     ❌ WRONG! Lost the docstring

# With @functools.wraps(func) ✅
# What Metadata Does It Copy?
# @functools.wraps(func) copies:

# __name__ — the function's name
# __doc__ — the docstring
# __module__ — which module it came from
# __qualname__ — qualified name
# __annotations__ — type hints
# __dict__ — custom attributes


import functools

def my_decorator(func):
    @functools.wraps(func)  # <-- This copies metadata from func to wrapper
    def wrapper(*args, **kwargs):
        print("Before calling function")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

print(greet.__name__)      # Output: greet         ✅ CORRECT!
print(greet.__doc__)       # Output: Say hello...  ✅ CORRECT!

print(greet("Alice"))  # Output: Before calling function \n Hello, Alice!
print(greet(name="Bob"))    # Output: Before calling function \n Hello, Bob!
