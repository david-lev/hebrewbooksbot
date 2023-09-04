import csv
import logging
from collections import defaultdict
from enum import Enum
from functools import lru_cache
from data.enums import Language

RTL = '\u200f'
LTR = '\u200e'


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
    START_CMD = 'START_CMD'
    START_CMD_DESC = 'START_CMD_DESC'
    CHANGE_LANG_CMD = 'CHANGE_LANG_CMD'
    CHANGE_LANG_CMD_DESC = 'CHANGE_LANG_CMD_DESC'
    STATS_CMD = 'STATS_CMD'
    STATS_CMD_DESC = 'STATS_CMD_DESC'
    BROWSE_CMD = 'BROWSE_CMD'
    BROWSE_CMD_DESC = 'BROWSE_CMD_DESC'
    SEARCH_CMD = 'SEARCH_CMD'
    SEARCH_CMD_DESC = 'SEARCH_CMD_DESC'
    CONTACT_US_CMD = 'CONTACT_US_CMD'
    CONTACT_US_CMD_DESC = 'CONTACT_US_CMD_DESC'
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
    CLICK_TO_REGISTER = 'CLICK_TO_REGISTER'
    NOT_REGISTERED_TITLE = 'NOT_REGISTERED_TITLE'
    NOT_REGISTERED_BODY = 'NOT_REGISTERED_BODY'
    CHOOSE_LANGUAGE = 'CHOOSE_LANGUAGE'
    CHANGE_LANGUAGE = 'CHANGE_LANGUAGE'
    LANGUAGE_CHANGED = 'LANGUAGE_CHANGED'
    SEARCHING_FOR_Q = 'SEARCHING_FOR_Q'
    NAVIGATE_BETWEEN_RESULTS = 'NAVIGATE_BETWEEN_RESULTS'
    BOT_UNDER_MAINTENANCE = 'BOT_UNDER_MAINTENANCE'
    FEATURE_UNDER_MAINTENANCE = 'FEATURE_UNDER_MAINTENANCE'
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
            try:
                key, lang, value = row
            except ValueError:
                raise ValueError(f'Invalid row: {row}')
            strings[String(key)][Language(lang)] = value
        return strings


_strings: dict[String, dict[Language, str]] = read_strings_from_csv('strings.csv')

for s in String:
    for l in Language:
        if l not in _strings[s]:
            logging.warning(f'String "{s}" is missing language "{l}"')


@lru_cache(maxsize=1_000)
def get_string(string: String, lng: Language, **kwargs) -> str:
    try:
        return (value := _strings[string].get(lng, _strings[string][Language.EN])).format(**kwargs)
    except KeyError:
        raise KeyError(f'String "{string}", language "{lng}", Kwargs: {kwargs}, Value: {value}')  # noqa
