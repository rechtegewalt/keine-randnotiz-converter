# Kleine Randnotiz converter

Converting data about right-wing incidents in Bremen, Germany as monitored by two NGOs on <https://keine-randnotiz.de>.

We use an internal API to transform the data into another data format. So technically, we are not scraping.

-   Website: <https://keine-randnotiz.de>
-   API: <https://keine-randnotiz.de/api/incidents>
-   Data: <https://morph.io/rechtegewalt/kleine-randnotiz-converter>

## Usage

For local development:

-   Install [poetry](https://python-poetry.org/)
-   `poetry install`
-   `poetry run python scraper.py`

For Morph:

-   `poetry export -f requirements.txt --output requirements.txt`
-   commit the `requirements.txt`
-   modify `runtime.txt`

## Morph

This is scraper runs on [morph.io](https://morph.io). To get started [see the documentation](https://morph.io/documentation).

## License

MIT
