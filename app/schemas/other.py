from pydantic import BaseModel


class TokenRefresh(BaseModel):
    pass  # Empty class since we'll use Authorization header
