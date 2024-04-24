import requests
from bs4 import BeautifulSoup


def get_pliego_pdf(href):
    html_text = requests.get(href)
    soup = BeautifulSoup(html_text.text, "lxml")
    anchors = soup.find_all("a")
    pliego_pdf = [
        anchor.get("href") for anchor in anchors if "liego" in anchor.get("href")
    ]
    return "https://www.hacienda.gob.es" + pliego_pdf[0]
