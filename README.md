# SCRAPING_FINCAS_HACIENDA
This project is designed to extract lands data from every auction that is published on [Hacienda](https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Patrimonio%20del%20Estado/Gestion%20Patrimonial%20del%20Estado/Paginas/Subastas/ListadoSubastasConcursos.aspx?den=&nat=&dels=). It also scrape a couple of auxiliar webs to get more information about each land.

## DESCRIPTION
The project has several internal packages that are tied together with the main runner package. Here's a brief overview of each package.
* **CATASTRO**: Several python files that given a "referencia catastral" scrape some web pages from Catastro website using Selenium. Besides retrieving the data directly from the HTML elements, it also downloads some files, such as PDF, KML and takes a screenshot.
* **INE**: Several python files that given a "referencia catastral" scrape some web pages from INE website using Selenium to get multiple data.  
* **CORREOS**: Python file that given the direction of a land scrape a web page from Correos website and returns the postal code, the province and the locality.
* **GOOGLE MAPS**: Python file that given two directions, it calculates the distance and time that takes from one point to the other. If only one direction is given, you can take a screenshot of the place.
* **HACIENDA**: Several python files that scrape some web pages from Hacienda website using BeautifulSoup, to get all the auctions published on the website, and for each one of them,
getting and processing the PDF that contains the info about the lands in auction.
* **SABI**: Python file that given a postal code scrape SABI database website using Selenium to get multiple data.

## Development Status
**Note:** THis project is currently under active development. Features and functionalities may change as development progresses.

## Current Progress

- [x] Get all the auctions announcements published on Hacienda.
- [x] Get and process the PDF that list the lands in auction for each auction announcement.
- [x] Get an array with all the lands in auction (referencia catastral and his price)
- [x] Given a reference catastral scrape multiple websites to get relevant data.
- [ ] Handle errors
- [ ] Save the retrieved data to a database.
- [ ] Check if the land in auction (referencia catastral) is already on the database, if so don't do anything else and jump to the next one.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details