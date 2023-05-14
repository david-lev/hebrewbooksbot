from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Letter:
    id: str
    name: str
    total: int


@dataclass(frozen=True, slots=True)
class DateRange:
    id: int
    name: str
    total: int


@dataclass(frozen=True, slots=True)
class Subject:
    id: int
    name: str
    total: int
    has_children: str  # y/n


@dataclass(slots=True)
class SearchResults:
    id: int
    title: str

    def __post_init__(self):
        self.id = int(self.id)


@dataclass(frozen=True, slots=True)
class Book:
    id: int
    title: str
    author: str
    city: str
    year: str
    pages: int
    new_reader_available: str  # true/false

    @property
    def pdf_url(self) -> str:
        """Get the book's PDF URL"""
        return f'https://download.hebrewbooks.org/downloadhandler.ashx?req={self.id}'

    def get_page_img(self, page: int, width: int, height: int) -> str:
        """
        Get the book's page image URL

        Args:
            page: The page number.
            width: The width of the image.
            height: The height of the image.
        """
        return f'https://beta.hebrewbooks.org/reader/pagepngs/{self.id}_{page}_{width}_{height}.png'

    def get_page_url(self, page: int) -> str:
        """
        Get the book's page URL

        Args:
            page: The page number.
        """
        return f'https://hebrewbooks.org/pdfpager.aspx?req={self.id}&pgnum={page}'
