from pydantic import BaseModel, computed_field

class JobApplication(BaseModel):
     full_name: str
     years_experience: int = 0

@computed_field
@property
def is_senior(self) -> bool:
    if self.years_experience <2:
         return 'junior'
    elif self.years_experience <5:
        return 'mid-level'

    return 'senior'
     

app= JobApplication(full_name="Rohan", years_experience=5, is_senior='mid-level')
print(app)

print(app.model_dump_json(indent=2))