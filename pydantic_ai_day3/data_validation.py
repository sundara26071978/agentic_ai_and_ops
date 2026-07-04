from typing import Annotated
from pydantic import BaseModel, Field

# Direct style
class JobApplicationV1(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    years_experience: int = Field(ge=0, le=50)
    # portfolio_url: str = Field(pattern=r"^https?://.*")

# # Annotated style — same behavior, more composable
class JobApplicationV2(BaseModel):
    full_name: Annotated[str, Field(min_length=2, max_length=100)]
    years_experience: Annotated[int, Field(ge=0, le=50)]
    email: Annotated[
        str,
        Field(description="Applicant's contact email", examples=["rohan@example.com"]),
    ]

job_data = {
    "full_name": "Ro", 
    "years_experience": 5,}
job_app_v1 = JobApplicationV1(**job_data)

print(job_app_v1)

job_data_annotated = {
    "full_name": "Ro",
    "years_experience": 5,
    "email": "rohanample.com"
}
job_app_v2 = JobApplicationV2(**job_data_annotated)

print(job_app_v2)


from pydantic import EmailStr


# # Annotated style — same behavior, more composable
class JobApplicationV3(BaseModel):
    full_name: Annotated[str, Field(min_length=2, max_length=100)]
    years_experience: Annotated[int, Field(ge=0, le=50)]
    # email: Annotated[
    #     EmailStr,
    #     Field(description="Applicant's contact email", examples=["rohan@example.com"]),
    # ]
    email : EmailStr

job_data_annotated = {
    "full_name": "Ro",
    "years_experience": 5,
    "email": "roha@nample.com"
}    


job_app_v3 = JobApplicationV3(**job_data_annotated)

print(job_app_v3.model_dump_json(indent=2))