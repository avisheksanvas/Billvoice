[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<br />
<p align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Bill-Voice</h3>

  <p align="center">
	An open source solution to all your inventory management and billing problems.
	Apart from that, a few DATA SCIENCE hacks to enhance your business.
  </p>
</p>



## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



## About The Project

[![Product Name Screen Shot1][productScreenshot1]]()
[![Product Name Screen Shot2][productScreenshot2]]()

This project is mainly built to help small and medium sized businesses maintain their stocks and create bills with a database based on Google Sheets. Aloing with that, it has a few other scripts that can help visualise potential orders to make that can increase profit, customers to look out for and more.

Here's what it can do:
* Create bills by searching products in the sheets that track stocks.
* Write each bill detail with customerName, date, total, etc. to a sheet that tracks sales.
* Update stocks each time products are sold.


### Built With
* [Python](https://www.python.org/)
* [Tkinter](https://docs.python.org/3/library/tkinter.html)
* [Matplotlib](https://matplotlib.org/)
* [Pandas](https://pandas.pydata.org/)



## Getting Started

There are a few things that will need to be setup to use this smoothly. Please follow instuctions as is.

### Google Sheets

* Create a spreadsheet which has 2 sheets ( with names - DETAIL and BROAD ( exact ) ) with the columns as given below. Lets call the spreadsheet **billSheet**.
[![BillSheet1][billSheet1]]()
[![BillSheet2][billSheet2]]()

* Create spreadsheets per brand ( of products ) with each spreadhseet having different sheets for orders made over time as. Lets call the below spreadsheet **stockSheet1**.
[![OrderSheet][orderSheet]]()

* Create a spreadsheet as below that will be used to track items that were not in stock but customer came to look for it. Lets call this spreadsheet **extraSheet**.
[![ExtraSheet][extraSheet]]()


### Installation

1. Clone the repo
```sh
git clone https://github.com/avisheksanvas/Billvoice.git
```
3. Install required packages in the local git directory
```sh
pip install tkinter
pip install google_spreadsheet
pip install google-auth-oauthlib
pip install pandas
pip install matplotlib
and so on for other packages you get an error for...
```


### Files to create in local git directory

**Make sure to place these files directly in the local directory that was created when you cloned**


* credentials.json
See **Step 1** of [Google Tutorial](https://developers.google.com/sheets/api/quickstart/python) to get the credentials.json file and and enable google sheets API.
* sheetData.py should be:
```python
# Say the sharing link to you spreadsheet is:
# https://docs.google.com/spreadsheets/d/<ID>/edit?usp=sharing
# Then ID is the spreadsheet ID


# billSheetID = ID of billSheet ( that we created above )
# extraSheetID = ID of extraSheet ( that we created above )
# stockSheet1ID = ID of stockSheet1 ( that we created above )
billSheetID = '<billSheetID>'
extraSheetID = '<extraSheetID>'
sheets = []
# orders should be equal to the number of ORDER sheets in each stock spreadsheet
sheets.append( { 'brand' : 'MAHINDRA',
                 'id' : '<stockSheet1ID>',
                 'orders' : 3 } )
sheets.append( { 'brand' : 'XYZ',
                 'id' : '<stockSheet2ID>',
                 'orders' : <noOfOrderSheetsForXYZ> } )
```


## Usage

* To run the billing software
```sh
python main.py
```
* To view a plot of the most sold products
```sh
python dataVisual.py
```


## How is Data Science involved?

### Create next order to make

### Create list of customers to look out for

## Roadmap

See the [open issues](https://github.com/avisheksanvas/Billvoice/issues) for a list of proposed features (and known issues).



## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



## License

Distributed under the MIT License. See `LICENSE` for more information.



## Contact

Your Name - [@avisheksanvas](https://twitter.com/avisheksanvas)




## Acknowledgements
* [Medium Blog For Google Sheet Iteraction](https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c)
* [Google Sheets Docs](https://developers.google.com/sheets/api/guides/values)





[contributors-shield]: https://img.shields.io/github/contributors/avisheksanvas/Billvoice.svg?style=flat-square
[contributors-url]: https://github.com/avisheksanvas/Billvoice/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/avisheksanvas/Billvoice.svg?style=flat-square
[forks-url]: https://github.com/avisheksanvas/Billvoice/network/members
[stars-shield]: https://img.shields.io/github/stars/avisheksanvas/Billvoice.svg?style=flat-square
[stars-url]: https://github.com/avisheksanvas/Billvoice/stargazers
[issues-shield]: https://img.shields.io/github/issues/avisheksanvas/Billvoice.svg?style=flat-square
[issues-url]: https://github.com/avisheksanvas/Billvoice/issues
[license-shield]: https://img.shields.io/github/license/avisheksanvas/Billvoice.svg?style=flat-square
[license-url]: https://github.com/avisheksanvas/Billvoice/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/avishek-santhaliya
[productScreenshot1]: images/productScreenshot1.png
[productScreenshot2]: images/productScreenshot2.png
[billSheet1]: images/billSheet1.png
[billSheet2]: images/billSheet2.png
[orderSheet]: images/orderSheet.png
[extraSheet]: images/extraSheet.png
