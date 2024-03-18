# This is a sample Python script.
import asyncio
import json

import aiohttp
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup

from models import Solution, PageObjectInterface, Singleton


# soup = soup.replace(nonBreakSpace, ' ')


# print(soup.title)
#
# # Getting the name of the tag
# # print(soup)
#
# # Getting the name of parent tag
# print(soup.title.parent.name)


class InterviewBitScraper(Singleton):

    def __init__(self):
        self.__session = None
        self.__name = "interview_bit_scrapper"
        self.__queue = []
        self.__offset = -1
        self.__parent_url = "https://www.interviewbit.com"
        self.problem_set_url_template = 'https://www.interviewbit.com/v2/problem_list/?page_offset={offset}'
        self.problem_page_url_template = 'https://www.interviewbit.com/v2/problems/{problem_name}/'
        self.hint_data_url_template = 'https://www.interviewbit.com/v2/problems/{problem_name}/hints/{hint_id}/'
        self.__headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Host": "www.interviewbit.com",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Cookie": """_ib_session=MGh3MGphbmo2VVEwZmZNb0NOUzE3TVc5eC8xeVd4M2Uyck43eExoYjVkeWNGM0Y1MTEvUDM2QUM5N2dXd2FxOXMxaEJldndpcmJnbTJLemRZNjhjbWpoQ1JOcTRnMDhwR0xJVHYwUFoxOHA0WlJOcUcyMmh5Wk1HVVBIbG5TODdEdUVCaFcwVjZzTXo1TW55bm4yTC9vdE1jeW5pbktTWmRFeTNFQ29IdVlOMUZnMW9NQUphNGs2MGtISlhXWE9JcWIxNnZWNldocEcrZGxYSEFCUlZrNHZLbUtlVWE2L3djdFBIZzRnOERwdXZsM1llVXhvcjdsYnFyV0dKUmU1TWJIT1RHWFFpWWhtNlB3WlFELzl4dlhobmdhcDZML2xZMFVQeFFyb2tWb1lYK3pMRmlmYkdvVXFvNGpjaG5Wb1dhYkl1TStCdzI1SklMZVd4TjVXaEhFZVluRy9Hem4xMEdpOTg5SGdLTlpoZWNZTFEybmRaYTE5QTVEZlYvclFuakpna2xCNmtOU2tNdnNnejRQQzFZSnJSSGZmQ0dRQ2FDVUxQUTNodWl6ZWJLQ2xhNDVBUU1sbWdDc0MvSWNOQTRrTmdMZERQWVllRzNqcVVaL0h4TDl0Mm9lSmNBRWtxdVRNUFhpWC9vQXZJdmRXVDhaMEFXa1FiOXJNMi90aGlZWjFobVQ0S2VHbjk5ZEFKNGZHdXJqSlhrbGNUdWlYNTdFd0dya3g3NHNlUm1GV3lBM3BsUEFzUjYwcU5GdkFjZHhlWU9hb3RWK2wzVm5QTjdJWEZmdTErVVZNZy8yNkcvaHRLR0FnYW8xMldpMjQzK1hiS0pHNjhPdE1ZVmRUZVE3aWdZbVgwbWYwZFRpc3pLMzBkdEE9PS0tUWgxcHVWNkZjWnJRUXY3SHczVGJYZz09--0540a59fa8a51898109d7610c170d3e5c2af78bf; XSRF-TOKEN=BlzdEdpDWZc4aAklvFwRAqy4aebyx9U3GXg3Jqzvyx6I6c3e8vQ1U4LICFGvx2EVy60NhDIGSONn%2F7zLz5J1yg%3D%3D; ahoy_visit=a325176d-7cb9-4ad5-b44d-325a82ac8c1f; ahoy_visitor=1a64f41d-a062-4f6e-be21-01526fc442f7; rubyenv_ts=2.5.9_2023-11-03T21%3A33%3A16%2B00%3A00"""
        }

    def __del__(self):
        asyncio.run(self.close_client_session())

    async def initiate_client_session(self):
        self.__session = aiohttp.ClientSession(headers=self.__headers)

    async def close_client_session(self):
        await self.__session.close()

    def get_url_for_scrap(self, number_of_urls: int) -> list[PageObjectInterface]:
        if len(self.__queue) >= number_of_urls:
            temp = self.__queue[:number_of_urls]
            self.__queue = self.__queue[number_of_urls:]

            return temp
        else:
            self.__offset = self.__offset + 1
            list_problem_url = self.problem_set_url_template.format(offset=self.__offset)
            r = requests.get(list_problem_url)
            problems = r.json()["items"]

        for problem in problems:
            problem_name = problem["slug"]

            # problem_data, err = self.__fetch_problem_data(problem_name)
            # description = self.__extract_description(problem_data)
            # hint_id = self.__extract_hint_id(problem_data)
            # hints_data, err = self.__fetch_hints_data(problem_name, hint_id)
            # code = self.__extract_code(hints_data)
            page_object = InterviewBitPage(url=self.problem_page_url_template.format(problem_name=problem_name),
                                           problem_name=problem_name)
            self.__queue.append(page_object)
        temp = self.__queue[:number_of_urls]
        self.__queue = self.__queue[number_of_urls:]

        return temp

    async def scrap_solution_for_problem(self, obj: PageObjectInterface, session) -> (Solution | None):
        if isinstance(obj, InterviewBitPage):
            try:
                problem_name = obj.get_problem_name()
                problem_data, err = await self.__fetch_problem_data(problem_name, session)
                description = self.__extract_description(problem_data)
                hint_id = self.__extract_hint_id(problem_data)
                hints_data, err = await self.__fetch_hints_data(problem_name, hint_id, session)
                code = self.__extract_code(hints_data)

                return Solution(url=self.problem_page_url_template.format(problem_name=problem_name),
                            description=description, code=code)
            except Exception as ex:
                print("interview bit scraper exp" + str(ex))
                return Solution(url=self.problem_page_url_template.format(problem_name=problem_name),
                                description=None, code=None)

        return None

    async def __fetch_problem_data(self, problem_name, session) -> (dict | None, Exception):
        if problem_name is not None:
            problem_url = self.problem_page_url_template.format(problem_name=problem_name)
            try:
                async with session.get(problem_url) as r:
                    if r.status in [200, 201]:
                        response = await r.json()
                        return response, None
                    else:
                        return None, None
            except Exception as ex:
                print(f"Error while fetching interview bit problem data for {problem_url} {ex}")
                return None, ex

    async def __fetch_hints_data(self, problem_name, hint_id, session) -> (dict, Exception):
        if problem_name is None or hint_id is None:
            return {}, None

        hint_url = self.hint_data_url_template.format(problem_name=problem_name, hint_id=hint_id)
        print(problem_name, hint_id, hint_url)
        try:
            # session.headers = headers
            if self.__session is None or self.__session.closed:
                await self.initiate_client_session()

            async with self.__session.get(url=hint_url) as res:
                if res.status in [200, 201]:
                    response = await res.json()
                    return response, None
                else:
                    return {}, None
        except Exception as ex:
            print(f"Error while fetching interview bit hints for {hint_url} {ex}")
            return {}, ex

    def __extract_description(self, problem_data: dict) -> (str | None):
        problem_description = None
        article = problem_data["article"]
        if article is not None and article["text"] is not None:
            problem_description = article["text"].lstrip("Problem Description ")

        return problem_description

    def __extract_hint_id(self, problem_data: dict) -> int | None:
        hints = problem_data["hints"]
        hint_id = None
        hints_list = []
        if hints is not None and hints["hints"] is not None:
            hints_list = hints["hints"]

        for hint in hints_list:
            if hint["title"] == "Complete Solution":
                hint_id = hint["id"]
                break

        if hint_id is None and hints["complete_solution"] is not None:
            complete_sol = hints["complete_solution"]
            hint_id = complete_sol.get("id")

        return hint_id

    def __extract_code(self, hints_data: dict) -> str | None:
        if "hint" not in hints_data:
            return None

        hint = hints_data["hint"]
        complete_sol = hint["complete_solution"]
        language_names = complete_sol.get("language_names", {})
        python_lang_id = None
        for lang_id, lang_name in language_names.items():
            if lang_name == "Python 3":
                python_lang_id = lang_id
                break

        if python_lang_id is not None:
            editorials = complete_sol["editorial_solutions"]
            python_content = editorials[python_lang_id]["content"]

            editorial_html = BeautifulSoup(python_content, 'html.parser')
            editorial_html.encode(formatter='html')

            return editorial_html.get_text()

        return None

    def get_parser_name(self) -> str:
        return self.__name


class InterviewBitPage(PageObjectInterface):
    def __init__(self, url, problem_name, description=None, code=None):
        self.__url = url
        self.__problem_name = problem_name
        self.__solution = Solution(url, description, code)
        self.__name = "interview_bit_solution"
        # self.__scrapper_instance = InterviewBitScraper()

    def get_name(self) -> str:
        return self.__name

    def get_url(self) -> str:
        return self.__url

    def get_result(self) -> (Solution | None):
        return self.__solution

    def get_problem_name(self) -> str:
        return self.__problem_name

    async def extract_code(self, session):
        return await self.__scrapper_instance.scrap_solution_for_problem(self, session)

# print(content)
# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     url_queue.append(parent_url)
#     for offset in range(1000):
#         description = None
#
#         list_problem_url = problem_set_url_template.format(offset=offset)
#         r = requests.get(list_problem_url)
#         problems = r.json()["items"]
#         for problem in problems:
#             problem_name = problem["slug"]
#             if problem_name is not None:
#                 problem_url = problem_page_url_template.format(problem_name=problem_name)
#                 r = requests.get(problem_url)
#                 response = r.json()
#
#                 article = response["article"]
#                 if article is not None and article["text"] is not None:
#                     description = article["text"].lstrip("Problem Description ")
#
#                 print(description)
#                 hints = response["hints"]
#                 hint_id = -1
#                 hints_list = []
#                 if hints is not None and hints["hints"] is not None:
#                     hints_list = hints["hints"]
#
#                 for hint in hints_list:
#                     if hint["title"] == "Complete Solution":
#                         hint_id = hint["id"]
#                         break
#
#                 if hint_id == -1 and hints["complete_solution"] is not None:
#                     complete_sol = hints["complete_solution"]
#                     hint_id = complete_sol.get("id", -1)
#
#                 if hint_id != -1:
#                     headers = {
#                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#                         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
#                         "Host": "www.interviewbit.com",
#                         "Accept-Language": "en-US,en;q=0.5",
#                         "Cache-Control": "no-cache",
#                         "Cookie": """_ib_session=MGh3MGphbmo2VVEwZmZNb0NOUzE3TVc5eC8xeVd4M2Uyck43eExoYjVkeWNGM0Y1MTEvUDM2QUM5N2dXd2FxOXMxaEJldndpcmJnbTJLemRZNjhjbWpoQ1JOcTRnMDhwR0xJVHYwUFoxOHA0WlJOcUcyMmh5Wk1HVVBIbG5TODdEdUVCaFcwVjZzTXo1TW55bm4yTC9vdE1jeW5pbktTWmRFeTNFQ29IdVlOMUZnMW9NQUphNGs2MGtISlhXWE9JcWIxNnZWNldocEcrZGxYSEFCUlZrNHZLbUtlVWE2L3djdFBIZzRnOERwdXZsM1llVXhvcjdsYnFyV0dKUmU1TWJIT1RHWFFpWWhtNlB3WlFELzl4dlhobmdhcDZML2xZMFVQeFFyb2tWb1lYK3pMRmlmYkdvVXFvNGpjaG5Wb1dhYkl1TStCdzI1SklMZVd4TjVXaEhFZVluRy9Hem4xMEdpOTg5SGdLTlpoZWNZTFEybmRaYTE5QTVEZlYvclFuakpna2xCNmtOU2tNdnNnejRQQzFZSnJSSGZmQ0dRQ2FDVUxQUTNodWl6ZWJLQ2xhNDVBUU1sbWdDc0MvSWNOQTRrTmdMZERQWVllRzNqcVVaL0h4TDl0Mm9lSmNBRWtxdVRNUFhpWC9vQXZJdmRXVDhaMEFXa1FiOXJNMi90aGlZWjFobVQ0S2VHbjk5ZEFKNGZHdXJqSlhrbGNUdWlYNTdFd0dya3g3NHNlUm1GV3lBM3BsUEFzUjYwcU5GdkFjZHhlWU9hb3RWK2wzVm5QTjdJWEZmdTErVVZNZy8yNkcvaHRLR0FnYW8xMldpMjQzK1hiS0pHNjhPdE1ZVmRUZVE3aWdZbVgwbWYwZFRpc3pLMzBkdEE9PS0tUWgxcHVWNkZjWnJRUXY3SHczVGJYZz09--0540a59fa8a51898109d7610c170d3e5c2af78bf; XSRF-TOKEN=BlzdEdpDWZc4aAklvFwRAqy4aebyx9U3GXg3Jqzvyx6I6c3e8vQ1U4LICFGvx2EVy60NhDIGSONn%2F7zLz5J1yg%3D%3D; ahoy_visit=a325176d-7cb9-4ad5-b44d-325a82ac8c1f; ahoy_visitor=1a64f41d-a062-4f6e-be21-01526fc442f7; rubyenv_ts=2.5.9_2023-11-03T21%3A33%3A16%2B00%3A00"""
#                     }
#                     hint_url1 = hint_data_url_template.format(problem_name=problem_name, hint_id=hint_id)
#                     print(problem_name, hint_id, hint_url1)
#                     r1 = None
#                     try:
#                         r1 = requests.get(hint_url1, headers=headers)
#                         r1.raise_for_status()
#                     except Exception as ex:
#                         pass
#                     res_json = r1.json()
#                     hint = res_json["hint"]
#                     complete_sol = hint["complete_solution"]
#                     language_names = complete_sol["language_names"]
#                     python_lang_id = -1
#                     for lang_id, lang_name in language_names.items():
#                         if lang_name == "Python 3":
#                             python_lang_id = lang_id
#                             break
#
#                     editorials = complete_sol["editorial_solutions"]
#                     python_content = editorials[python_lang_id]["content"]
#
#                     editorial_html = BeautifulSoup(python_content, 'html.parser')
#                     editorial_html.encode(formatter='html')
#
#                     print(editorial_html.get_text())
#                 else:
#                     pass
#
#         # url = url_queue.popleft()
#         # print(
#         #     f"stats queue size {len(url_queue)}  dlq size {len(dlq)}  url archives {len(url_archives)}  extracted codes {len(extract_pages)}")
#         # # r = requests.get(url)
#         # soup = BeautifulSoup(r.content, 'html.parser')
#         # soup.encode(formatter='html')
#         # code_blocks = extract_code_container_from_web_page(soup)
#         # if code_blocks is None:
#         #     dlq.append(url)
#         #     print("URL does not have any code blocks" + url)
#         # else:
#         #     extract_pages[soup.title.string] = code_blocks
#
#         # if len(extract_pages.keys()) >= 100:
#         #     with open("url_archive.json", "w+") as fp:
#         #         json.dump(url_archives, fp)
#         #
#         #     with open("dlq.json", "w") as fp:
#         #         json.dump(dlq, fp)
#         #
#         #     with open("extracted_code.json", "w") as fp:
#         #         json.dump(extract_pages, fp)
#         #
#         #     with open("queued_url.json", "w") as fp:
#         #         json.dump({"queue": [*url_queue]}, fp)
#         #
#         #     break
#         #
#         # retrieve_all_valid_links_from_page(soup)
