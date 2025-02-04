# DjangoTrader

Created by Kyle Peeler

## Overview

My fourth coding project: A stock trading website designed using Python Django
That allows users to create accounts and buy/sell stock using funds deposited into the accounts.

Used to learn and display knowledge of Python and Django.

## Details

* Navbar containing account information. changes dependent on whether user is logged in or not.
* Home page that displays a stock chart created with Chart.js fed info from Yahoo Finance.
* Home page also displays portfolio information including stock owned, price of stock owned, buttons to quickly buy and sell stock and total portfolio value.
* Portfolio system displayed using javascript to dynamically update information without resetting page.
* A stock trading system allowing users to input a symbol, buy stock based on the current price from Yahoo Finance, and sell stock to have money from the trade returned.
* An account system allowing users to keep track of their individual portfolio and balances.
* A demonstation deposit system allowing users to deposit simulated money for transactions.

## Usage

Source code hosted at <https://github.com/Kpeeler51/DjangoTrader>

Demo website hosted at <https://djangotrader.onrender.com>

* enter homepage and input desired stock symbol for information
* Click register button and input user information to register for an account.
* After logging into account enter desposit page and input desired cash value.
* Return to home page and purchase desired stock. Portfolio will be updated accordingly
* Use portfolio buttons to quickly buy or sell owned stock.

### To run locally:

* Pull the source code from github using git pull
* Running the build.sh script in the terminal will install requirements and migrate database.
* Go into settings.py and set debug mode to true.
* Enter python manage.py runserver into terminal.
* Website address will be displayed in the terminal.

## Technologies Used

HTML5, CSS3, Javascript, Chart.js, Yahoo Finance API, Django, Python, VSCode, Render for hosting.

## Future improvements

A in depth deposit system using paypal or other financial options.

Better usage of Django forms.

Improve account system using email verification and two step authentication.

Improve modular setup and systems for better reusability and maintainability.