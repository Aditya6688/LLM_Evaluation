import requests
from bs4 import BeautifulSoup


def scrape_url(url: str) -> dict:
    """Scrape a web page and return its title and body text."""
    response = requests.get(url, timeout=10, headers={"User-Agent": "LLM-Eval-Bot/1.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    text = soup.get_text(separator="\n", strip=True)

    return {"url": url, "title": title, "text": text}
