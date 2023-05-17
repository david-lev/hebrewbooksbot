from dataclasses import dataclass
from data.enums import BrowseType as BrowseTypeEnum


class CallbackData:
    """
    Base class for callback data classes
    """
    __clbname__: str  # Must be overridden in subclasses

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def from_callback(
            cls,
            callback_data: str,
            sep: str = ':',
    ) -> 'CallbackData':
        """
        Convert a callback string to a CallbackData object

        - Important: The order of the fields in the callback string must match the order of the fields in the class!!

        Args:
            callback_data: The callback string (e.g. "browse_nav:subject:342:5:10")
            sep: The separator between the fields in the callback string (default: ':')
        """
        if not callback_data.startswith(cls.__clbname__):
            raise ValueError(f"Invalid callback data: {callback_data}")
        try:
            return cls(*(
                annotation(value) for annotation, value in zip(
                    cls.__annotations__.values(),
                    callback_data.split(sep)[1:],
                    strict=True
                )
            ))
        except ValueError as e:
            raise ValueError(f"Invalid callback data: {callback_data}") from e

    def to_callback(self, sep: str = ':') -> str:
        """
        Convert the object to a callback string

        Args:
            sep: The separator between the fields in the callback string (default: ':')
        """
        return sep.join([self.__clbname__, *(str(getattr(self, field)) for field in self.__annotations__)])

    def join_to_callback(self, *others, sep: str = ',', clb_sep: str = ':') -> str:
        """
        Join the callback data with other callback data

        Args:
            others: Other ``CallbackData`` objects or strings
            sep: The separator between the callback strings (default: ',')
            clb_sep: The separator between the fields in the callback fields (default: ':')
        """
        return sep.join([
            self.to_callback(),
            *(other.to_callback(sep=clb_sep) if isinstance(other, CallbackData) else other for other in others)
        ])


@dataclass(frozen=True, slots=True)
class BrowseNavigation(CallbackData):
    __clbname__ = 'browse_nav'
    type: BrowseTypeEnum
    id: str
    offset: int
    total: int


@dataclass(frozen=True, slots=True)
class BrowseType(CallbackData):
    __clbname__ = 'browse_type'
    type: BrowseTypeEnum


@dataclass(frozen=True, slots=True)
class SearchNavigation(CallbackData):
    __clbname__ = 'search_nav'
    offset: int
    total: int


@dataclass(frozen=True, slots=True)
class ShowBook(CallbackData):
    __clbname__ = 'show'
    id: int


@dataclass(frozen=True, slots=True)
class ReadBook(CallbackData):
    __clbname__ = 'read'
    id: int
    page: int
    total: int


@dataclass(frozen=True, slots=True)
class JumpToPage(CallbackData):
    __clbname__ = 'jump'
    id: int
    page: int
    total: int