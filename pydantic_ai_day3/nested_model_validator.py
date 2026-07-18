from pydantic import BaseModel, Field, ValidationError

# 1. Define the Child Model
class Address(BaseModel):
    city: str
    zipcode: int = Field(gt=0, description="Zipcode must be positive")

# 2. Define the Parent Model with Nesting
class User(BaseModel):
    name: str
    address: Address  # Nested model

# --- Scenario A: Successful Validation ---
valid_data = {
    "name": "Alice",
    "address": {
        "city": "Gotham",
        "zipcode": "12345"  # Pydantic will coerce this string to an int
    }
}

user = User(**valid_data)
print(user.address.zipcode)  # Output: 12345 (as an integer)


# --- Scenario B: Validation Failure ---
invalid_data = {
    "name": "Bob",
    "address": {
        "city": "Metropolis",
        "zipcode": "not-a-number"  # This will fail
    }
}

try:
    User(**invalid_data)
except ValidationError as e:
    print(e)