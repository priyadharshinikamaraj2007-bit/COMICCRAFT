from pydantic import BaseModel, Field, field_validator

class ComicRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=3000)
    character_name: str = Field(default="Alex", max_length=80)
    setting: str = Field(default="forest", max_length=120)
    tone: str = Field(default="dramatic", max_length=60)
    art_style: str = Field(default="comic book", max_length=80)

    @field_validator("prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value

class ImageTestRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
