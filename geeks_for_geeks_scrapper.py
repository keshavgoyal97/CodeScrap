from bs4 import BeautifulSoup
import pygtrie
from pytrie import SortedStringTrie as Trie

from models import PageObjectInterface, Solution, ScrapInterface, Singleton


class GeeksForGeeksPage(PageObjectInterface):

    def __init__(self, url, description=None, code=None):
        self.__url = url
        self.__solution = Solution(url=url, description=description, code=code)
        self.__name = "geeks_for_geeks_solution"
        # self.__scrapper_instance = GeeksForGeeksScraper()

    def get_name(self) -> str:
        return self.__name

    def get_url(self) -> str:
        return self.__url

    def get_result(self) -> (Solution | None):
        return self.__solution

    async def extract_code(self, session):
        return await self.__scrapper_instance.scrap_solution_for_problem(self, session)


class GeeksForGeeksScraper(Singleton):

    def __init__(self):
        self.__name = "geeks_for_geeks"
        self.__parent_url = "https://www.geeksforgeeks.org"
        self.__queue = [GeeksForGeeksPage(url=self.__parent_url)]
        self.__url_archives = Trie()

    def get_url_for_scrap(self, number_of_urls: int) -> list[PageObjectInterface]:
        if len(self.__queue) >= number_of_urls:
            temp = self.__queue[:number_of_urls]
            self.__queue = self.__queue[number_of_urls:]
            return temp
        else:
            temp = self.__queue
            self.__queue = []
            return temp

    def get_parser_name(self) -> str:
        return self.__name

    async def scrap_solution_for_problem(self, obj: PageObjectInterface, session) -> (Solution, Exception):
        r, err = await self.__fetch_page_data(session, obj.get_url())
        if r is None:
            return Solution(url=obj.get_url(), code=None, description=None), None

        soup = BeautifulSoup(r, 'html.parser')
        soup.encode(formatter='html')
        code_blocks = self.__extract_code_container_from_web_page(soup)
        self.__retrieve_all_valid_links_from_page(soup)

        return Solution(url=obj.get_url(), description=soup.title.string, code=code_blocks)

    async def __fetch_page_data(self, session, url):
        print(url)
        try:
            async with session.get(url) as res:
                if res.status in [200, 201]:
                    response = await res.text()
                    return response, None
                else:
                    return None, None
        except Exception as exp:
            print(f"Error while fetching gforg page for {url} {exp}")
            return None, exp

    def __valid_tag(self, element):
        return False if element.name is None else True

    def __extract_code_from_code_container(self, html_element):
        code = ""

        for child in html_element:
            if self.__valid_tag(child):
                code = code + child.get_text().replace('\xa0', ' ') + "\n"

        return code

    def __extract_code_container_from_web_page(self, element):
        s = element.findAll('div', class_='code-block')
        if len(s) == 0:
            return None

        python_code_versions = []
        for s1 in s:
            i_ele = s1.find(lang="python3")
            if i_ele is not None:
                # print(s1)

                # print(s1.contents[3])
                code_block = s1.find("div", class_="container")
                # if code_block.contents[3] == " ":
                # print(len(code_block.contents[5].text))
                python_code_versions.append(self.__extract_code_from_code_container(code_block).replace('"', "'"))

        return python_code_versions

    def __retrieve_all_valid_links_from_page(self, soup):
        a_tags = soup.findAll('a')
        for a_tag in a_tags:
            if a_tag.has_attr('href'):
                link = a_tag["href"]
                link = link.removesuffix('/')
                # index_link = link.removeprefix(self.__parent_url)
                if link.startswith(self.__parent_url) and not self.__url_archives.has_key(link):
                    page_object = GeeksForGeeksPage(url=link)
                    self.__queue.append(page_object)
                    self.__url_archives[link] = 1
