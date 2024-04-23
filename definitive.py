from auctions import get_all_auctions_urls
from auction import get_pliego_pdf


def main():
    auctions = get_all_auctions_urls()
    pliegos_pdf = [get_pliego_pdf(auction) for auction in auctions]
    print(pliegos_pdf[0])


if __name__ == "__main__":
    main()
