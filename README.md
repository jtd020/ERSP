# Web Scraping Tool for Collecting Data on the Visited Links Feature

This tool is used to go through a large set of websites where for each website, the script will determine whether the feature is enabled. The script determines the presense of the feature by comparing before and after screenshots.

The script is built with Selenium and Python in order to iterate through websites and uses cv2 in order to compare images.

In order to run the script, first install the required packages, Firefox, and GeckoDriver. Then, run the python filed named click_link_test.py from the command. 

The script takes a csv file of websites, which includes the ranking of the website on the first column and the associated website in the second. The csv can be inserted by passing in the file path into the command line.

## Guides
    https://www.seleniumhq.org/docs/

## Requirements
    Python 3
    Selenium
    Firefox
    Geckodriver

## Installation
### Installing Geckodriver:
	Latest Version of Geckodriver:
		https://github.com/mozilla/geckodriver/releases
	Guide:
		Linux:
			https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu
		Windows:
			https://www.softwaretestinghelp.com/geckodriver-selenium-tutorial/

### Installing Firefox:
	https://www.mozilla.org/en-US/firefox/new/





