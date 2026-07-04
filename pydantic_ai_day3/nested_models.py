from pydantic import BaseModel

class Address(BaseModel):
    city: str
    state: str
    pin_code: str

class Applicant(BaseModel):
    name: str
    email: str
    address: Address        # a whole model, used as a field type

# Parsing straight from a nested dictionary — the common real-world case
incoming = {
    "name": "Rohan Mehta",
    "email": "rohan@example.com",
    "address": {"city": "Pune", "state": "Maharashtra", "pin_code": "411001"},
}



applicant = Applicant.model_validate(incoming)
print(applicant.address.city)   # "Pune" — dot-chain access, fully typed

applicant = Applicant(**incoming)   # unpacking the dict into the model constructor
print(applicant.address.city)   # "Pune" — dot-chain access, fully typed




# Lists of nested models work the same way
class WorkExperience(BaseModel):
    company: str
    role: str
    years: int

class Application(BaseModel):
    applicant: Applicant
    work_history: list[WorkExperience]