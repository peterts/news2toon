from pydantic import BaseModel, Field, conlist


class SpeechBubble(BaseModel):
    person: str = Field(..., alias="Person")
    text: str = Field(..., alias="Tekst")

    @property
    def is_narrator(self) -> bool:
        return self.person == "Fortellerstemme"

    @property
    def full_text(self) -> str:
        if self.is_narrator:
            return self.text
        return f"{self.person}: {self.text}"

    @property
    def person_prefix(self) -> str:
        return f"{self.person}: "

    def remove_person_prefix(self, full_text: str) -> str:
        return full_text.removeprefix(self.person_prefix)


class CartoonStripCell(BaseModel):
    speech_bubbles: list[SpeechBubble] = Field(..., alias="Snakkebobler")
    image_description: str = Field(..., alias="Bildebeskrivelse")
    image_url: str | None = Field(None, alias="Bildelenke")


class CartoonStrip(BaseModel):
    title: str = Field(..., alias="Tittel")
    cells: conlist(CartoonStripCell, min_length=4, max_length=4) = Field(
        ..., alias="Bilder"
    )
