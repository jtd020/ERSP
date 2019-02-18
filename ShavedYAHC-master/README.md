# ShavedYAHC

> Streamlined version of the [YAHC web crawler](https://github.com/gakiwate/yahc)

**TODO:** Rewrite README. The original YAHC readme is reproduced below.

---

This crawler was primarily designed for research work done at UCSD.

## Goals
Specifically, we want the crawler to mantain high-fidelity and provide
capabilities that typical crawlers may not to do.

* Map hostnames to specific IPs
* Know DNS mapping when crawling
* Save cookies
* Follow redirections
* Take screenshots
* Capture state
* Capture resources requested
* Work with multiple browsers

## Design
Based on previous experience, we wanted to stay away from specific
browser ecosystems and deal with add-ons to achieve the above goals.

Additionally, we wanted a design where we can give the crawler only
the privileges of a normal user and expect it to do all of the above.

The "crawler" is built on top of the "selenium" project. This helps
us easily achieve most of the goals above. However, one key
capability that it did not buy us was the ability to map hostnames
to specific IPs.

Given that we do not want to grant the crawler additonal privileges
to be able to do this, we add a proxy layer on top of the selenium
driver which we can then use to make connections to specific IP
addresses for hostnames.

Note, that the proxy server is tightly coupled with the crawler. Hence,
every instance of the crawler will have it's own proxy.

## How To
Hopefully, the installation should be simple. You can simply
download and install yahc with the following steps

### Download
```
git clone git@github.com:gakiwate/yahc.git
```
or
```
git clone https://github.com/gakiwate/yahc.git
```

### Install
Installation is a two step process. You will need to have pip installed.
```
cd yahc
pip install .
```

You will need to download the binaries for selenium to run. Currently, yahc supports
chrome and firefox. We use chromedriver and geckodriver binaries for the crawler.

You can download the chrome - [chromdriver binary from here](https://sites.google.com/a/chromium.org/chromedriver/downloads)
You can download the firefox - [geckodriver binary from here](https://github.com/mozilla/geckodriver/releases)

### Setup
Make sure that your path includes the binaries that you download in the step above
```
export PATH="/path_to_binary:"$PATH
```
Ideally, you should put this in your *~/.bashrc*

### Run
You can simply run using the following command
```
yahc --urls "http://www.example.com" --store-location "/tmp"
```

You can change the store-location to any absolute path.

To enable taking *snapshots* and save *cookies* run
```
yahc --urls "http://www.example.com" --store-location "/tmp" --take-screenshot --save-cookies
```

### Code Changes
You can make changes to the code. For them to take effect you can upgrade using pip
```
pip install . --upgrade
```
