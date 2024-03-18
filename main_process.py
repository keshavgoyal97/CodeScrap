import asyncio
import json
from collections import deque
from signal import SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM, signal

import aiohttp

from geeks_for_geeks_scrapper import GeeksForGeeksScraper
from main_interview_bit import InterviewBitScraper, InterviewBitPage

# class ScrapInterface:
#     def get_parser_name(self) -> str:
#         pass
#
#     def get_url_for_scrap(self, number_of_urls: int) -> list[PageObjectInterface]:
#         pass


# interview bit parser
# get urls
# take from queue or call end point and return object(get_url, extract_code)
# restore state


url_queue = deque()
extract_pages = {}
dlq = []
dlq_page_num = 0
extract_page_num = 0

scrapers = [InterviewBitScraper(), GeeksForGeeksScraper()]


async def main():
    global dlq, extract_pages, extract_page_num, dlq_page_num
    count = 0
    while count < 1000:
        try:
            # for scraper in scrapers:
            url_queue.extend(scrapers[0].get_url_for_scrap(20))
            url_queue.extend(scrapers[1].get_url_for_scrap(100))

            tasks = []
            async with aiohttp.ClientSession() as session:
                while len(url_queue) > 0:
                    url = url_queue.pop()
                    if isinstance(url, InterviewBitPage):
                        tasks.append(asyncio.ensure_future(scrapers[0].scrap_solution_for_problem(url, session)))
                    else:
                        tasks.append(asyncio.ensure_future(scrapers[1].scrap_solution_for_problem(url, session)))

                results = await asyncio.gather(*tasks, return_exceptions=False)
                for result in results:
                    if result.get_description() is None or result.get_code() is None:
                        dlq.append(result.get_url())
                        if len(dlq) >= 2000:
                            with open(f"dlq_page_{dlq_page_num}.json", "w") as fp:
                                json.dump({"dlq_data": dlq}, fp)
                            dlq = []
                            dlq_page_num = dlq_page_num + 1
                    else:
                        extract_pages[result.get_description()] = result.get_code()

                        if len(extract_pages) >= 500:
                            with open(f"extracted_code_page{extract_page_num}.json", "w") as fp:
                                json.dump(extract_pages, fp)
                            extract_pages = {}
                            extract_page_num = extract_page_num + 1
            if count % 100 == 0:
                await asyncio.sleep(1)
            count = count + 1
        except Exception as exp:
            print("Exception " + str(exp))

    with open("extracted_code.json", "w") as fp:
        json.dump(extract_pages, fp)


def store():
    with open("extracted_code.json", "w") as fp:
        json.dump(extract_pages, fp)


for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
    signal(sig, store)

if __name__ == '__main__':
    asyncio.run(main())
