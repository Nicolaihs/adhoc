import time
import requests
from typing import List, IO
import click
from tqdm import tqdm
from urllib.parse import quote

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Cookie": 'CookieInformerBooklet=hidden; _ga=GA1.2.937225194.1514890816; __utma=265959761.310459757.1525698137.1618483257.1618513881.1320; I18N_LANGUAGE="da"; fullscreenMode=',
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


@click.command()
@click.argument("input_file", type=click.File("r"))
@click.option(
    "--delay", type=float, default=1, help="Delay (in seconds) between each lookup."
)
@click.option(
    "--start-row", type=int, default=0, help="Starting row in the input file."
)
@click.option(
    "--base-urls",
    type=str,
    default="https://ordnet.dk/ddo/ordbog?query={word}",
    help="Comma separated list of base URLs to lookup. Use {word} for place where query word should be inserted. Default: https://ordnet.dk/ddo/ordbog?={word}. Example: https://ordnet.dk/ddo/ordbog?={word},https://ordnet.dk/ddo/ordbog/?query={word}",
)
def main(
    input_file: IO[str],
    delay: float,
    start_row: int,
    base_urls: str = "https://ordnet.dk/ddo/ordbog?query={word}",
) -> None:
    word_list = parse_words(input_file)
    lookup_urls(word_list, base_urls, delay, start_row)


def parse_words(input_file: IO[str]) -> List[str]:
    """Parse words from input file

    Args:
        input_file: filepath for input file

    Returns:
        a list of words
    """
    words = []
    for line in input_file:
        line_words = line.strip().split(",")
        words.extend(line_words)
    words = [word for word in words if word]
    return words


def lookup_urls(words: List[str], base_urls: str, delay: float, start_row: int) -> None:
    """Create URLs and lookup each of them

    Args:
        words: a list of words
        base_urls: base URLs to lookup, comma separated
        delay: the delay between each lookup
        start_row: which row to start from
    """

    def get_capitalized(word: str) -> str:
        if len(word) == 0:
            return word  # return an empty string if the word is empty
        return word[0].upper() + word[1:]

    words = words[start_row:]

    # Add capitalized version
    new_words = []
    for word in words:
        new_words.append(word)
        new_words.append(get_capitalized(word))
    words = new_words

    # Add quoted versions
    new_words = []
    for word in words:
        new_words.append(word)
        if " " in word:
            new_words.append(word.replace(" ", "+"))
        if quote(word) != word:
            new_words.append(quote(word))

    words = new_words
    words = list(set(words))

    print(f"Total number of words to lookup: {len(words)}")
    print(f"Lookup delay: {delay} seconds")
    print(f"Looking up these base_urls: {base_urls}")

    base_url_list = base_urls.split(",")

    progress_bar = tqdm(
        total=len(words) * len(base_url_list),
        desc="URL",
        unit="url",
        leave=True,
        ncols=150,
    )

    varnish_count = 0
    total_requests = 0
    for word in words:
        for base_url in base_url_list:
            url = base_url.format(word=word)
            response = requests.get(url, headers=HEADERS, timeout=5)

            if "X-Varnish" in response.headers and "X-Cache" in response.headers:
                cache_status = response.headers["X-Cache"]
                if cache_status.lower() == "hit":
                    varnish_count += 1
            else:
                cache_status = "Not served by Varnish"

            total_requests += 1
            progress_bar.set_postfix_str(
                f"Current: {word} | Cache status: {cache_status} | Varnish: {varnish_count} of {total_requests} requests",
                refresh=True,
            )

            progress_bar.update(1)
            time.sleep(delay)

    progress_bar.close()


if __name__ == "__main__":
    main()
