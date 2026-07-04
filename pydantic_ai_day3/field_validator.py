from pydantic import BaseModel, EmailStr, ValidationError, Field, field_validator, model_validator


class Applicant(BaseModel):
    name: str
    email: EmailStr


valid_applicant = Applicant(name="Rohan", email="rohan@yopmail.com")
print("Valid:", valid_applicant, "\n")



class JobApplication(BaseModel):
    full_name: str
    email: EmailStr
    years_experience: str ="0"


    @field_validator('email')
    @classmethod
    def reject_disposable_domains(cls,value:str)->str:

      blocked_domain = {'yopmail.com','tempmail.com','mailinator.com'}
      user_domain = value.split('@')[-1].lower()

      if user_domain in blocked_domain:
            raise ValueError(f"disposable email domains are not accepted ({user_domain})")

      return value.lower()
    

    @field_validator("years_experience")
    @classmethod
    def strip_years_suffix(cls, value):
        """
        Handles input like "5 years" or "5yrs" arriving as raw text —
        common when scraping form data or parsing free-text resumes —
        by stripping non-numeric junk BEFORE the int type-check runs.
        """
        if isinstance(value, str):
            digits_only = "".join(ch for ch in value if ch.isdigit())
            return int(digits_only) if digits_only else value
        return value
    

# valid_applicant = JobApplication(full_name="Rohan", email="rohan@yopmail.com")
# print("Valid:", valid_applicant, "\n")


valid_applicant = JobApplication(full_name="Rohan", email="rohan@yopmsaail.com", years_experience="5yrs")
print("Valid:", valid_applicant, "\n")