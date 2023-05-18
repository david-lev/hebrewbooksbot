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


@dataclass(frozen=True, slots=True)
class Section:
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class PageContent:
    gmara: list[Section]
    rashi: list[Section] | None = None
    tosfot: list[Section] | None = None


@dataclass(frozen=True, slots=True)
class MasechetPage:
    str_id: str
    masechet_id: int
    name: str
    content: PageContent | None = None

    @property
    def id(self):
        """Get the page ID"""
        if self.str_id.endswith('b'):
            num = int(self.str_id[:-1]) + 1
            return (num - 2) + (num - 2)
        else:
            return (int(self.str_id) - 2) + (int(self.str_id) - 1)

    @property
    def pdf_url(self) -> str:
        """Get the page's PDF URL"""
        return f'https://beta.hebrewbooks.org/pagefeed/hebrewbooks_org_{self.masechet_id}_{self.id}.pdf'


@dataclass(frozen=True, slots=True)
class Masechet:
    id: int
    name: str
    pages: list[MasechetPage] | None = None

    @property
    def total(self):
        """Get the masechet's total pages"""
        return len(self.pages) if self.pages else None


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
