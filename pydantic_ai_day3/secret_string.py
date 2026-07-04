from pydantic import BaseModel, SecretStr


class UserAccount(BaseModel):
    username: str
    password: SecretStr

account = UserAccount(username="rohan99", password="super-secret-123")
print(account)                              # password shows as **********
print(account.password.get_secret_value())