from Catastro.catastro_report import CatastroReport

land = "8878009FE0087N0001HJ"

catastro_land_report = CatastroReport(land, "Rústica")
catastro_land_report.land_first_page()
catastro_land_report.close_cookies()
catastro_land_report.land_query_value_page()
catastro_land_report.access_with_dni()
catastro_land_report.select_date_and_property()
reference_value = catastro_land_report.get_reference_value_amount()
catastro_land_report.get_reference_value_report()
