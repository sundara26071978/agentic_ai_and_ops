from pydantic import BaseModel, model_validator, SecretStr,ValidationError, field_validator

class SignupForm(BaseModel):
    username: str
    password: SecretStr
    confirm_password: SecretStr

    @field_validator('password')
    @classmethod
    def reject_disposable_domains(cls,value:str)->str:
      if len(value)<8:
        raise ValidationError

      return value.lower()



    @field_validator('confirm_password')
    @classmethod
    def reject_disposable_domains(cls,value:str)->str:
      if len(value)<8:
        raise ValidationError

      return value.lower()

    @model_validator(mode="after")
    def passwords_must_match(self):
        if SecretStr(self.password) != SecretStr(self.confirm_password):
            raise ValueError("password and confirm_password do not match")
        return self

signup_form = SignupForm(username="rohan99", password=SecretStr("super-secret-123"), confirm_password=SecretStr("super-secret-123"))
print("Valid:", signup_form, "\n")

signup_form = SignupForm(username="rohan99", password=SecretStr("super-secret-123"), confirm_password=SecretStr("super-secret=-123"))
print("Invalid:", signup_form, "\n")


# A richer example — mutually exclusive preferences
class JobApplication(BaseModel):
    remote_preferred: bool
    willing_to_relocate: bool

    @model_validator(mode="after")
    def check_relocation_logic(self):
        if self.remote_preferred and self.willing_to_relocate:
            raise ValueError("Can't be both remote-only AND willing to relocate")
        return self