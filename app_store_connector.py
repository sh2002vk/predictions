import re
import requests
from bs4 import BeautifulSoup
import urllib3

# Optional: silence the LibreSSL warning
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

headers = {
    # Pretend to be a normal browser so Apple doesn't get suspicious
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )
}


def get_top_apps(category="UNPAID", count=30):
    # category options: PAID/UNPAID

    if category == "PAID":
        URL = "https://apps.apple.com/us/iphone/charts/36?chart=top-paid"
    elif category == "UNPAID":
        URL = "https://apps.apple.com/us/iphone/charts/36?chart=top-free"
    else:
        return

    resp = requests.get(URL, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    app_links = []

    # Grab all anchor tags that look like app detail links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.match(r"^https://apps\.apple\.com/us/app/.+/id\d+$", href):
            text = " ".join(a.stripped_strings)
            if not text:
                continue
            app_links.append((href, text))

    # De-duplicate and keep order
    seen = set()
    apps = []
    for href, text in app_links:
        if href in seen:
            continue
        seen.add(href)

        # Text often ends with " View" – trim that off if present
        if " View" in text:
            text = text.rsplit(" View", 1)[0]

        # Try to parse "1 Shadowrocket Rule based proxy utility"
        parts = text.split(" ", 1)
        rank = None
        name = text

        if parts[0].isdigit():
            rank = int(parts[0])

        temp_name = re.search(r"/us/app/([^/]+)/id\d+", href)
        if (temp_name):
            name = temp_name.group(1).replace("-", " ")

        apps.append(
            {
                "rank": rank,
                "name": name
            }
        )

    # Limit to requested count
    return apps[:count]

if __name__ == "__main__":
    # Example usage
    bets = get_top_apps("UNPAID")

    # Print each bet on its own line
    for bet in bets:
        print(bet)
