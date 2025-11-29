from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    
    class Config:
        from_attributes = True