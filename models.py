class Solution:
    def __init__(self, url: str, description: str | None, code: object):
        self.__url = url
        self.__code = code
        self.__description = description

    def get_code(self) -> object:
        return self.__code

    def get_description(self) -> str:
        return self.__description

    def get_url(self) -> str:
        return self.__url


class PageObjectInterface:
    def get_result(self) -> (str | None, Exception):
        pass

    def get_url(self) -> str:
        pass

    def get_name(self) -> str:
        pass

    async def extract_code(self, session):
        pass


class ScrapInterface:
    def get_parser_name(self) -> str:
        pass

    def get_url_for_scrap(self, number_of_urls: int) -> list[PageObjectInterface]:
        pass

    def scrap_solution_for_problem(cls, PageObjectInterface, session) -> (Solution, Exception):
        pass


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance
