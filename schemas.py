from pydantic import BaseModel, Field


class RecogidaEntrada(BaseModel):
    sku: str = Field(min_length=1)
    cantidad: int = Field(gt=0, strict=True)