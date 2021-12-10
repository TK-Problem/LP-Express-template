# LP-Express template

Python dash app to entry packages from `Etsy` website to `LP-Express`.

App demo is hosted on Heroku:

* https://lp-express-template.herokuapp.com/

## Project structure

* `app.py` main dash app file to run server.
* `layouts.py` contains layouts for the app.
* `Procfile` server location for Heroku.
* `runtime.txt` defines Python version for Heroku.
* `assets` folder contains .css files and app logo.

## Requirements

All requirements are listed in `requirements.txt` file. Main libraries:

* `dash`- app layout,
* `pandas`- data cleaning,
* `pyppeteer`- remote data entry.