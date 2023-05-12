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


@dataclass(slots=True)
class Subject:
    id: int
    name: str
    total: int
    has_children: bool

    def __post_init__(self):
        self.has_children = self.has_children == 'y'


@dataclass(slots=True)
class SearchResults:
    id: int
    title: str

    def __post_init__(self):
        self.id = int(self.id)

    @property
    def cover_url(self) -> str:
        """Get the book's cover URL"""
        return self.get_page_url(page=1, width=100, height=100)

    @property
    def pdf_url(self) -> str:
        """Get the book's PDF URL"""
        return f'https://download.hebrewbooks.org/downloadhandler.ashx?req={self.id}'

    def get_page_url(self, page: int, width: int = 600, height: int = 800) -> str:
        return f'https://beta.hebrewbooks.org/reader/pagepngs/{self.id}_{page}_{width}_{height}.png'




@dataclass(slots=True)
class Book:
    id: int
    title: str
    author: str
    city: str
    year: str
    pages: int
    new_reader_available: bool

    def __post_init__(self):
        self.new_reader_available = self.new_reader_available == 'true'

    @property
    def cover_url(self) -> str:
        """Get the book's cover URL"""
        return self.get_page_url(page=1, width=100, height=100)

    @property
    def pdf_url(self) -> str:
        """Get the book's PDF URL"""
        return f'https://download.hebrewbooks.org/downloadhandler.ashx?req={self.id}'

    def get_page_url(self, page: int, width: int = 600, height: int = 800) -> str:
        return f'https://beta.hebrewbooks.org/reader/pagepngs/{self.id}_{page}_{width}_{height}.png'
