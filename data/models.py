from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Letter:
    id: str
    name: str
    total: int

    @property
    def has_children(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class DateRange:
    id: int
    name: str
    total: int

    @property
    def has_children(self) -> bool:
        return False


@dataclass(slots=True)
class Subject:
    id: int
    name: str
    total: int
    has_children: bool

    def __post_init__(self):
        self.has_children = False


@dataclass(frozen=True, slots=True)
class Tursa:
    id: str
    name: str
    has_children: bool

    @property
    def total(self) -> int:
        """Only for compatibility with BrowseType"""
        return 0

    @property
    def pdf_url(self):
        """Get the page PDF url
        """
        return f"https://beta.hebrewbooks.org/tursa/{self.id}.pdf"

    @property
    def url(self):
        """Get the read page url"""
        return f"https://beta.hebrewbooks.org/tursa.aspx?a={self.id}"


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
    read_id: str
    masechet_id: int
    masechet_read_id: int
    name: str
    content: PageContent | None = None

    @property
    def id(self):
        """Get the page ID"""
        if self.read_id.endswith('b'):
            num = int(self.read_id[:-1]) + 1
            return (num - 2) + (num - 2)
        else:
            return (int(self.read_id) - 2) + (int(self.read_id) - 1)

    @property
    def pdf_url(self) -> str:
        """Get the page's PDF URL"""
        return f'https://beta.hebrewbooks.org/pagefeed/hebrewbooks_org_{self.masechet_id}_{self.id}.pdf'

    def get_page_img(self, width: int, height: int) -> str:
        """
        Get the page's image URL

        Args:
            width: The width of the image.
            height: The height of the image.
        """
        return f'https://beta.hebrewbooks.org/reader/pagepngs/{self.masechet_id}_{self.id}_{width}_{height}.png'

    def get_page_url(self, fmt: str = 'pdf') -> str:
        """
        Get the masechet page's url

        Args:
            fmt: The format of the page (pdf, or text)
        """
        return f'https://hebrewbooks.org/shas.aspx?mesechta={self.masechet_read_id}&daf={self.read_id}&format={fmt}'


@dataclass(frozen=True, slots=True)
class MasechetBase:
    """Masechet with id using for read request, not the book id"""
    id: int
    name: str

    @property
    def total(self) -> int:
        """Only for compatibility with BrowseType"""
        return 0


@dataclass(frozen=True, slots=True)
class Masechet:
    id: int
    read_id: int
    name: str
    pages: list[MasechetPage]

    @property
    def total(self) -> int:
        """Get the total number of pages"""
        return len(self.pages)


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

    def _validate_page(self, page: int) -> None:
        if page < 1 or page > self.pages:
            raise ValueError(f'Page number must be between 1 and {self.pages}')

    def get_page_img(self, page: int, width: int, height: int) -> str:
        """
        Get the book's page image URL

        Args:
            page: The page number.
            width: The width of the image.
            height: The height of the image.
        """
        self._validate_page(page)
        return f'https://beta.hebrewbooks.org/reader/pagepngs/{self.id}_{page}_{width}_{height}.png'

    def get_page_pdf(self, page: int) -> str:
        """
        Get the book's page PDF URL

        Args:
            page: The page number.
        """
        self._validate_page(page)
        return f'https://beta.hebrewbooks.org/pagefeed/hebrewbooks_org_{self.id}_{page}.pdf'

    def get_page_url(self, page: int) -> str:
        """
        Get the book's page URL

        Args:
            page: The page number.
        """
        self._validate_page(page)
        return f'https://hebrewbooks.org/pdfpager.aspx?req={self.id}&pgnum={page}'
