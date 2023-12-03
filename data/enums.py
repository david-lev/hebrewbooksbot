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


class BookType(BaseEnum):
    BOOK = "b"
    MASECHET = "m"
    TURSA = "t"


class ReadMode(BaseEnum):
    PDF = "p"
    IMAGE = "i"
    TEXT = "t"


class Language(Enum):
    # CONST -> (CODE, NAME, FLAG, RTL)
    EN = ("en", "English", "🇺🇸", False)
    HE = ("he", "עברית", "🇮🇱", True)
    FR = ("fr", "Français", "🇫🇷", False)
    ES = ("es", "Español", "🇪🇸", False)
    YI = ("yi", "ייִדיש", "🔯", True)

    def __new__(cls, *values):
        obj = object.__new__(cls)
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values
        return obj

    @classmethod
    def from_code(cls, code: str):
        try:
            return cls(code)
        except ValueError:
            return cls.EN

    def __repr__(self):
        return f"{self.flag}"

    @property
    def code(self) -> str:
        return self._all_values[0]

    @property
    def name(self) -> str:
        return self._all_values[1]

    @property
    def flag(self) -> str:
        return self._all_values[2]

    @property
    def rtl(self) -> bool:
        return self._all_values[3]
