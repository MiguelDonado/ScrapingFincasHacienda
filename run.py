from scrape.catastro import Catastro

item = Catastro()
item.land_first_page()
item.search("15083G512013510000TH")
item.go_to_otros_visores()
item.download_kml()
