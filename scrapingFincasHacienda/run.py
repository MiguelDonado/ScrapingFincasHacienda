from GoogleMaps.GoogleMaps import GoogleMaps

item = GoogleMaps(
    None,
    """42.74920155490726, -8.56230785817032""",
)
item.land_first_page()
item.close_cookies()
item.search_to()
item.get_screenshot()
