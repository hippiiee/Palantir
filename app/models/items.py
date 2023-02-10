from typing import Optional, List, Any
from pydantic import validator, BaseModel

class GithubUser(BaseModel):
    url : str
    name : str
    email : Optional[str]
    private_url : Optional[str]
    location : Optional[str]
    twitter_username : Optional[str]
    nb_followers : Optional[int]
    nb_following : Optional[int]
    starred : List[str] = []
    followers : List[str] = []
    following : List[str] = []

    @validator("url")
    def url_must_be_valid(cls, v):
        if not v.startswith("https://github.com/"):
            raise ValueError("Invalid url")
    
class Repository(BaseModel):
    """Repository model"""
    url : str
    name : Optional[str]
    author : Optional[str]
    nb_stars : Optional[int]
    stargazers : Optional[List[GithubUser]]
    
    @validator("url")
    def url_must_be_valid(cls, v):
        if not v.startswith("https://github.com/"):
            raise ValueError("Invalid url")


def custom_encoder(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return {k: custom_encoder(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [custom_encoder(x) for x in obj]
    elif isinstance(obj, str):
        return f'"{obj}"'
    elif obj is None:
        return 'null'
    else:
        return obj