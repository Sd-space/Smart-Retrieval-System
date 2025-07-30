from pydantic import BaseModel, HttpUrl
from typing import List

class DocumentRequest(BaseModel):
    documents: HttpUrl

class ParsedResponse(BaseModel):
    chunks: List[str]
