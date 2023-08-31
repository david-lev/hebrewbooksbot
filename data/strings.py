import csv
import sys
from collections import defaultdict
from enum import Enum
from functools import lru_cache

RTL = '\u200f'
LTR = '\u200e'


class Language(Enum):
    # CONST -> (CODE, NAME, FLAG, RTL)
    EN = ('en', 'English', '🇺🇸', False)
    HE = ('he', 'עברית', '🇮🇱', True)
    FR = ('fr', 'Français', '🇫🇷', False)
    ES = ('es', 'Español', '🇪🇸', False)

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
        return f'{self.flag}'

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


class String(str, Enum):
    TG_WELCOME = 'TG_WELCOME'
    WA_WELCOME_HEADER = 'WA_WELCOME_HEADER'
    WA_WELCOME_BODY = 'WA_WELCOME_BODY'
    IN_MEMORY_FOOTER = 'IN_MEMORY_FOOTER'
    SEARCH = 'SEARCH'
    SEARCH_INSTRUCTIONS = 'SEARCH_INSTRUCTIONS'
    SEARCH_IN_CHATS = 'SEARCH_IN_CHATS'
    BROWSE = 'BROWSE'
    INSTANT_READ = 'INSTANT_READ'
    BACK = 'BACK'
    GITHUB = 'GITHUB'
    ABOUT = 'ABOUT'
    WA_ABOUT_MSG = 'WA_ABOUT_MSG'
    PYWA_CREDIT = 'PYWA_CREDIT'
    HEBREWBOOKS_SITE = 'HEBREWBOOKS_SITE'
    STATS = 'STATS'
    SHOW_STATS = 'SHOW_STATS'
    SHOW_STATS_ADMIN = 'SHOW_STATS_ADMIN'
    SHARE = 'SHARE'
    DOWNLOAD = 'DOWNLOAD'
    NEXT = 'NEXT'
    PREVIOUS = 'PREVIOUS'
    WAIT_FOR_PREVIEW = 'WAIT_FOR_PREVIEW'
    PAGE_X_OF_Y = 'PAGE_X_OF_Y'
    READ_ON_SITE = 'READ_ON_SITE'
    SLOW_DOWN = 'SLOW_DOWN'
    PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y = 'PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y'
    NUMBERS_ONLY = 'NUMBERS_ONLY'
    JUMP_TIP = 'JUMP_TIP'
    JUMP_ALSO_BY_EDIT_TIP = 'JUMP_ALSO_BY_EDIT_TIP'
    NO_BOOK_SELECTED = 'NO_BOOK_SELECTED'
    CHOOSE_BROWSE_TYPE = 'CHOOSE_BROWSE_TYPE'
    SHAS = 'SHAS'
    SHAS_CMD = 'SHAS_CMD'
    TUR_AND_SA = 'TUR_AND_SA'
    TUR_AND_SA_CMD = 'TUR_AND_SA_CMD'
    SUBJECTS = 'SUBJECTS'
    SUBJECTS_CMD = 'SUBJECTS_CMD'
    LETTERS = 'LETTERS'
    LETTERS_CMD = 'LETTERS_CMD'
    DATE_RANGES = 'DATE_RANGES'
    DATE_RANGES_CMD = 'DATE_RANGES_CMD'
    CHOOSE = 'CHOOSE'
    CHOOSE_LETTER = 'CHOOSE_LETTER'
    CHOOSE_SUBJECT = 'CHOOSE_SUBJECT'
    CHOOSE_DATE_RANGE = 'CHOOSE_DATE_RANGE'
    CHOOSE_MASECHET = 'CHOOSE_MASECHET'
    START_SEARCH_INLINE = 'START_SEARCH_INLINE'
    SEARCH_TIP = 'SEARCH_TIP'
    BOOK_NOT_FOUND = 'BOOK_NOT_FOUND'
    MASECHET_NOT_FOUND = 'MASECHET_NOT_FOUND'
    PRESS_TO_SHARE = 'PRESS_TO_SHARE'
    SEARCH_RESULTS = 'SEARCH_RESULTS'
    X_RESULTS_FOR_S = 'X_RESULTS_FOR_S'
    X_TO_Y_OF_TOTAL_FOR_S = 'X_TO_Y_OF_TOTAL_FOR_S'
    X_TO_Y_OF_TOTAL = 'X_TO_Y_OF_TOTAL'
    NO_RESULTS_FOR_Q = 'NO_RESULTS_FOR_Q'
    SEARCH_INLINE = 'SEARCH_INLINE'
    ORIGINAL_SEARCH_DELETED = 'ORIGINAL_SEARCH_DELETED'
    IMAGE = 'IMAGE'
    DOCUMENT = 'DOCUMENT'
    TEXT = 'TEXT'
    NOT_REGISTERED = 'NOT_REGISTERED'
    CHOOSE_LANGUAGE = 'CHOOSE_LANGUAGE'
    CHANGE_LANGUAGE = 'CHANGE_LANGUAGE'
    LANGUAGE_CHANGED = 'LANGUAGE_CHANGED'
    SEARCHING_FOR_Q = 'SEARCHING_FOR_Q'
    NAVIGATE_BETWEEN_RESULTS = 'NAVIGATE_BETWEEN_RESULTS'
    UNDER_MAINTENANCE = 'UNDER_MAINTENANCE'
    WAIT_X_SECONDS = 'WAIT_X_SECONDS'
    WAIT_X_MINUTES = 'WAIT_X_MINUTES'
    X_IS_UPLOADED = 'X_IS_UPLOADED'
    RESEARCH = 'RESEARCH'

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'


def read_strings_from_csv(filename: str) -> dict[String, dict[Language, str]]:
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        strings = defaultdict(dict)
        for row in reader:
            if row[0] == 'Key':
                continue
            key, lang, value = row
            strings[String(key)][Language(lang)] = value
        return strings


_strings = read_strings_from_csv('strings.csv')

for s in _strings:
    for lang in Language:
        if lang not in _strings[s]:
            print(f'"{lang.name}" is missing for "{s.name}"')
            # sys.exit(1)


@lru_cache(maxsize=None)
def get_string(string: String, lng: Language, **kwargs) -> str:
    return _strings[string][lng].format(**kwargs)
