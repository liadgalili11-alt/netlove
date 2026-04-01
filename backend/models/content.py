from pydantic import BaseModel, Field


class GeneratedContent(BaseModel):
    hook: str = Field(default="", description="כותרת ראשית מושכת")
    caption: str = Field(default="", description="מלל שיווקי מפורט")
    hashtags: list[str] = Field(default_factory=list, description="רשימת האשטאגים")
