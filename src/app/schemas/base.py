from pydantic import BaseModel

class OurBaseModel(BaseModel ):
    class Config:
        from_attributes = True

class OurBaseModelOut(OurBaseModel):
    message: str | None
    status: int | None

class PagedResponse(OurBaseModelOut):
    page_number: int | None
    page_size: int | None
    total_pages: int | None
    total_records: int | None

