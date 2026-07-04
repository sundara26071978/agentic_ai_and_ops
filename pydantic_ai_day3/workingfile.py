def register_user(name, email, age):
    """
    Registers a user and calculates the year they were born.
    Notice: there is NOTHING here telling Python what types these
    parameters are supposed to be. Nothing stops the caller from
    passing garbage.
    """
    birth_year = 2026 - age  # <-- this line silently assumes `age` is an int
    print(f"Registered {name} ({email}), born approx. {birth_year}")


good_form_data = {"name": "Aditi", "email": "aditi@example.com", "age": 28}
register_user(**good_form_data)

print("\n=== Now let's see what happens with bad data ===")


bad_form_data = {"name": "Rohan", "email": "rohan@example.com", "age": 10000}
register_user(**bad_form_data)

name : str = "Alice"

tags: list[str] = ["python", "pydantic", "fastapi"]
quantities: list[int] = [1, 5, 3, 2]
word_counts: dict[str, int] = {"error": 12, "warning": 5}
settings: dict[str, str] = {"theme": "dark", "language": "en"}

print(tags, quantities, word_counts, settings)

print("\n=== Now let's see what happens with bad data ===")




class FormData:
    def __init__(self, name: str, email: str, age: int, message: str = "Hello"):
        self.name = name
        self.email = email
        self.age = age
        self.message = message



sunjform_data = FormData(name="Sunj", email="sunj@example.com", age=25, message="Hi there!")


print(f"Name: {sunjform_data.name}, Email: {sunjform_data.email}, Age: {sunjform_data.age}, Message: {sunjform_data.message}")



from dataclasses import dataclass

@dataclass
class FormDataDataclass:
    name: str
    email: str
    age: int
    message: str = "Hello"  


sunjform_dataclass = FormDataDataclass(name="Sunj", email="sunj@example.com", age=25, message="Hi there!")

print(f"Name: {sunjform_dataclass.name}, Email: {sunjform_dataclass.email}, Age: {sunjform_dataclass.age}, Message: {sunjform_dataclass.message}")


from pydantic import BaseModel


class FormDataPydantic(BaseModel):
    name: str
    email: str
    age: int
    message: str = "Hello"

sunjform_pydantic = FormDataPydantic(name="Sunj", email="sunj@example.com", age=25, message="Hi there!")
print(f"Name: {sunjform_pydantic.name}, Email: {sunjform_pydantic.email}, Age: {sunjform_pydantic.age}, Message: {sunjform_pydantic.message}")


sunjform_pydantic1  = FormDataPydantic(name="Sunj", email="sunj@example.com", age="28", message="Hi there!")

print(f"Name: {sunjform_pydantic1.name}, Email: {sunjform_pydantic1.email}, Age: {sunjform_pydantic1.age}, Message: {sunjform_pydantic1.message}")


# sunjform_pydantic2  = FormDataPydantic(name="Sunj", email="sunj@example.com", age="twentyfive", message="Hi there!")

# print(f"Name: {sunjform_pydantic2.name}, Email: {sunjform_pydantic2.email}, Age: {sunjform_pydantic2.age}, Message: {sunjform_pydantic2.message}")



from pydantic import ValidationError

class SignUpForm(BaseModel):
    username: str
    password: str
    email: str
    newsletter: bool = False


incoming_data = {
    "username": "new_user",
    "password": "secure_password",
    "email": "new_user@example.com"
}

try:
    form = SignUpForm(**incoming_data)
    print("Form data is valid.")
except ValidationError as e:
    print("Form data is invalid.")
    print(e)


second_incoming_data = {
    "username": "new_user"}

try:
    form = SignUpForm(**second_incoming_data)
    print("Form data is valid.")
except ValidationError as e:
    print("Form data is invalid.")
    print(e)


user_1_data = {"name": "mayank",  "age": "28","is_interested":"True"}

class SignupForm2(BaseModel):
  name : str
  age : int
  is_interested : bool


user_1 = SignupForm2(**user_1_data)

print(user_1)