from enum import Enum


class BaseEnum(str, Enum):
    def __str__(self):
        return self.value


class BrowseType(BaseEnum):
    SUBJECT = "subject"
    LETTER = "letter"
    DATERANGE = "daterange"
    SHAS = "s"
    TURSA = "t"
