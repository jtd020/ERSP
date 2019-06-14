import csv
import multiprocessing
import sys
import argparse

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

import cv2
import numpy as np
import os
import shutil
import time

animation_success_count = 0
total_valid_urls = 0
failed_animation_removal_list = []
broken_url_list = []
error_403_url_list = []


def main(url_list, headless=True):
    """
    Description:
        Cleans, scrapes, and clicks every link on a given URL
    Args:
        url: url of string to scrape
        image_location: string path to image file in system.
        headless: determines whether to run browser in headless mode
    Returns:
        String
    """

    url = url_list[0]
    image_location = url_list[1]
    rank = url_list[2]
    detected = False
    num_links = 0

    if not make_directory(image_location):
        return str(rank) + " " + url + " " + str(detected)

    options = Options()
    if headless:
        options.headless = True

    browser_profile = webdriver.FirefoxProfile()
    # browser_profile.add_extension(extension='adblock_plus-3.5.2-an+fx.xpi')
    # browser_profile.set_preference("extensions.adblockplus.currentVersion", "3.5.2")
    browser_profile.set_preference("dom.webnotifications.enabled", False)

    for retry in range(0,100):
        try:
            driver = webdriver.Firefox(options=options, firefox_profile=browser_profile)
            break
        except:
            sys.stdout.flush()
            if retry == 99:
                print(str(rank) + " " + url + " failed_driver" + " " + str(num_links))
                return str(rank) + " " + url + " failed_driver" + " " + str(num_links)
            continue
    # driver.set_page_load_timeout(30)
    # driver.install_addon(os.path.dirname(__file__) + r'\\adblock_plus-3.5.2-an+fx.xpi', temporary=True)

    try:
        driver.get(url)
    except:
        sys.stdout.flush()
        print(str(rank) + " " + url + " " + " failed_url" + " " + str(num_links))
        driver.quit()
        return str(rank) + " " + url + " failed_url" + " " + str(num_links)
    print (str(len(driver.find_elements_by_tag_name("a"))) + url)
    wait = WebDriverWait(driver, 10)
    driver.execute_script("""
        var items = document.getElementsByTagName("a");
        Array.from(items).forEach(function(item){
            var attributes = Object.values(item.attributes);
            for (i=0; i < attributes.length; i++) {
                if (attributes[i].nodeName.toString() != "href" && attributes[i].nodeName.toString() != "class") {
                    item.removeAttribute(attributes[i].nodeName.toString());
                }
            }
            item.setAttribute("target", "_blank");
    });""")
    num_minutes = 60 * 2
    try:
        remove_animations(driver, num_minutes, str(url[12:]))
    except:
        try:
            driver.quit()
        except:
            print ("Driver cannot close")
        print(str(rank) + " " + url + " " + " failed_animation" + " " + str(num_links))
        return str(rank) + " " + url + " failed_animation" + " " + str(num_links)

    driver.maximize_window()

    # changes all links open in new tabs

    if "403 Forbidden" in driver.page_source:
        error_403_url_list.append(url)
        sys.stdout.flush()
        print (str(rank) + " " + url + " failed_403" + " " + str(num_links))
        driver.quit()
        return str(rank) + " " + url + " failed_403" + " " + str(num_links)

    elements = driver.find_elements_by_tag_name("a")
    count = 0
    num_links = len(elements)
    prev_sec = time.time()
    timeout = 60 * 4
    for i in range(0, len(elements)):
        if timeout < (time.time() - prev_sec):
            break
        count += 1

        el = elements[i]
        try:
            if not switch_to_old_window(driver):
                break
            # skip element without href attribute
            if el.get_attribute("href") is None:
                continue

            # skip element that's an anchor or has calls a javascript function
            href = parse_outer_html_href(el)
            if href[0:1] == "#" or "javascript" in href:
                continue

            # skip element that is not displayed
            if not el.is_displayed():
                continue

            # check if element is not enabled
            if not el.is_enabled():
                ActionChains(driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).send_keys(
                    Keys.ESCAPE).perform()
                continue

            location = el.location
            size = el.size
            if timeout < (time.time() - prev_sec):
                break
            before = take_screenshot(driver.get_screenshot_as_png(), location, size, "before" + str(count),
                                     image_location)

            # clicks on link
            ActionChains(driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).send_keys(Keys.ESCAPE).perform()
            # driver.implicitly_wait(10)

            blank_element = driver.find_element_by_tag_name("body")
            ActionChains(driver).context_click(blank_element).perform()
            # ActionChains(driver).move_to_element(el).move_by_offset(location['x']*(-1), location['y']*(-1)).perform()
            time.sleep(2)

            if timeout < (time.time() - prev_sec):
                break

            if not switch_to_old_window(driver):
                break
            # driver.implicitly_wait(10)
            # driver.implicitly_wait(10)

            delete_all_tabs(driver)

            if timeout < (time.time() - prev_sec):
                break

            ActionChains(driver).move_to_element(el)
            if not switch_to_old_window(driver):
                break

            # re-grab element location on screen
            location = el.location
            if timeout < (time.time() - prev_sec):
                break

            if not el.is_displayed():
                continue

            after = take_screenshot(driver.get_screenshot_as_png(), location, size, "after" + str(count), image_location)

        except Exception as e:
            # delete_all_tabs(driver)
            # driver.implicitly_wait(5)
            if timeout < (time.time() - prev_sec):
                break
            if not switch_to_old_window(driver):
                break
            continue

        if timeout < (time.time() - prev_sec):
            break
        if not make_directory("comparison_" + ''.join(e for e in url if e.isalnum()) +"/"):
            break

        if compare_images(before, after, "comparision_" + ''.join(e for e in url if e.isalnum()),
                          "comparison_" + ''.join(e for e in url if e.isalnum()) +"/"):
            detected = True
            print("Feature detected")
            break
    #     os.remove(before)
    #     os.remove(after)
    #
    # shutil.rmtree(image_location)
    sys.stdout.flush()
    print(str(rank) + " " + url + " " + str(detected) + " " + str(num_links))
    driver.quit()
    return str(rank) + " " + url + " " + str(detected) + " " + str(num_links)


def delete_all_tabs(driver):
    original_handle = driver.window_handles[0]
    for handle in driver.window_handles:
        if handle != original_handle:
            driver.switch_to.window(handle)
            driver.close()


def take_screenshot(image, location, size, name, image_location):
    im = Image.open(BytesIO(image))

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))

    im.save(image_location + name + ".png")
    return str(image_location + name + ".png")


def compare_images(before, after, name, image_location):
    before_image = cv2.imread(before)
    after_image = cv2.imread(after)
    difference = cv2.subtract(after_image, before_image)
    result = not np.any(difference)
    if result:
        return False
    else:
        cv2.imwrite(image_location + "result" + name + ".png", difference)
        # cv2.imwrite(image_location + "before" + name + ".png", before_image)
        # cv2.imwrite(image_location + "after" + name + ".png", after_image)
        return True


def resize_image(image_location, new_size):
    """
    Description:
        Resizes the image in the given path to a new size.
    Args:
        image_location: string path to image file in system.
	new_size:       image size dictionary, e.g ['width': 0, 'height': 0]
    Returns:
        Nothing.
    """
    if not os.path.exists(image_location):
        return
    size = new_size['width'], new_size['height']
    im = Image.open(image_location)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(image_location)


def remove_animations(driver, timeout, url):
    """
    Description:
        Removes animated objects on website using image differencing.
    Args:
        driver:  Firefox browser.
	timeout: function timeout in seconds.
    Returns:
        Nothing.
    """
    count_timeout = 5
    no_animation_count = 0
    prev_sec = time.time()
    curr_sec = prev_sec

    driver.implicitly_wait(timeout * 2)

    remove_all_tags(driver, "video")
    remove_all_tags(driver, "img")
    remove_cursor_flickering(driver)

    # attempt to remove animated elements
    while timeout > curr_sec - prev_sec and no_animation_count < count_timeout:
        if animation_detected(driver, ''.join(e for e in url if e.isalnum())):
            if timeout < time.time() - prev_sec:
                break
            remove_animated_element(driver, "animation_" + ''.join(e for e in url if e.isalnum()),
                                    "animation/" + "animation_" + ''.join(e for e in url if e.isalnum()) + "/")
            if timeout < time.time() - prev_sec:
                break
            no_animation_count = 0
        curr_sec = time.time()
        no_animation_count += 1


def animation_detected(driver, url, delay_sec=1):
    """
    Description:
        Removes animated objects on website using image differencing.
    Args:
        driver:  Firefox browser.
	delay_sec: Seconds delay between the before and after screenshot.
    Returns:
        True if the before and after screenshot are different, False otherwise.
    """
    make_directory("animation/" + "animation_" + url + "/")
    location = {'x': 0, 'y': 0}
    window_size = driver.get_window_size()
    before = take_screenshot(driver.get_screenshot_as_png(), location, window_size, "animation_before" + url,
                             "animation/" + "animation_" + url + "/")
    time.sleep(delay_sec)
    after = take_screenshot(driver.get_screenshot_as_png(), location, window_size, "animation_after" + url,
                            "animation/" + "animation_" + url + "/")
    return compare_images(before, after, "animation_" + url, "animation/" + "animation_" + url + "/")


def remove_animated_element(driver, name, image_location):
    """
    Description:
        From the image differencing algorithm, this function finds the first
        (x,y) coordinate that is flagged as different then maps the coordinate
	to the browser window such that the animated element being removed must
	contain (x, y).
    Args:
        driver: Firefox browser
    Returns:
        Nothing.
    """
    if not os.path.exists(image_location + "result" + name + ".png"):
        return

    resize_image(image_location + "result" + name + ".png", driver.get_window_size())
    im = Image.open(image_location + "result" + name + ".png")
    width = im.size[0]
    height = im.size[1]
    pixel = im.load()

    # skip (0,0) because of non-visible elements like scripts.
    for x in range(1, width):
        for y in range(1, height):
            if pixel[x, y] != (0, 0, 0):
                # image difference pixel - critical pixel
                if remove_element_at(driver, x, y):
                    print("animation element deleted")
                return


def remove_element_at(driver, x, y):
    """
    Description:
        Removes a root element that contains the given (x,y) coordinate.
    Args:
        driver: Firefox browser.
	x:      x coordinate conatined in desired element.
	y:      y coordinate contained in desired element.
    Returns:
        True if an element was removed, False otherwise.
    """
    # print("at (" + str(x) + ", " + str(y) + ")")
    web_elements = driver.find_elements_by_tag_name("*")
    for el in web_elements:
        try:
            tag_name = driver.execute_script("return arguments[0].tagName", el);
            el_has_children = driver.execute_script("return arguments[0].children.length != 0", el)
            parent = driver.execute_script("return arguments[0].parentNode", el)
            parent_name = driver.execute_script("return arguments[0].tagName", parent);

            if el_has_children:
                continue

            if in_element_bounds(el, x, y) or (parent_name != "BODY" and in_element_bounds(parent, x, y)):
                print(tag_name)
                delete_element(driver, el)
                return True
        except:
            continue
    return False


def delete_element(driver, el):
    """
    Description:
        Deletes an element from DOC HTML.
    Args:
        driver: Firefox browser.
	el:     element to be removed.
    Returns:
        Nothing.
    """
    driver.execute_script('''
        var element = arguments[0];
        element.parentNode.removeChild(element);
    ''', el);


def in_element_bounds(el, x, y):
    """
    Description:
      Checks if (x,y) is in the in the rectangular bounds of the given element.
    Args:
        el: element of interest.
	x:  horizontal inquiry location
	y:  horizontal inquirt location
    Returns:
        True if (x,y) is exists on the given element, False otherwise.
    """
    if x >= el.location['x'] and x <= el.location['x'] + el.size['width']:
        if y >= el.location['y'] and y <= el.location['y'] + el.size['height']:
            return True
    return False


def remove_all_tags(driver, tag):
    """
    Description:
        Removes all tags from HTML DOM.
    Args:
      driver: Firefox browser.
    Returns:
        Nothing.
    """
    video_elements = driver.find_elements_by_tag_name(tag)
    for video in video_elements:
        try:
            delete_element(driver, video)
        except:
            continue


def remove_cursor_flickering(driver):
    """
    Description:
        Blurs the the active element animation
    Args:
      driver: Firefox browser.
    Returns:
        Nothing.
    """
    driver.execute_script("document.activeElement.blur();");


def close_browser(driver):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        driver.close()


def make_directory(image_location):
    for retry in range(100):
        try:
            if os.path.exists(image_location):
                shutil.rmtree(image_location)
            os.mkdir(image_location)
            return True
            break
        except:
            continue
    return False


def switch_to_old_window(driver):
    for retry in range(100):
        try:
            driver.switch_to.window(driver.window_handles[0])
            return True
            break
        except:
            continue
    return False

def parse_outer_html_href(el):
    soup = BeautifulSoup(el.get_attribute("outerHTML"), features="html.parser")
    href = ""
    for a in soup.find_all('a', href=True):
        href = a["href"]
    return href


def print_stats_report(invalid_url_list):
    global total_valid_urls
    global animation_success_count
    global error_403_count
    total_invalid_urls = len(invalid_url_list)

    if total_valid_urls == 0:
        return

    print("\n----------------- Statistics Report -----------------")
    print("animation removal sucess rate: " + str(animation_success_count / total_valid_urls * 100) + "%")
    print("total websites: " + str(total_valid_urls + total_invalid_urls))
    print("valid websites: " + str(total_valid_urls))
    print("invalid websites due to incorrect protocol: " + str(total_invalid_urls - error_403_count))
    print("forbidden websites (error 403) : " + str(error_403_count))
    print("percent of invalid websites encountered: " + str(
        total_invalid_urls / (total_valid_urls + total_invalid_urls) * 100) + "%")
    print("invalid url list:")
    for url in invalid_url_list:
        print(url)
    print("-----------------------------------------------------\n")

def test_403(url_list):
    """
        Description:
            Cleans, scrapes, and clicks every link on a given URL
        Args:
            url: url of string to scrape
            image_location: string path to image file in system.
            headless: determines whether to run browser in headless mode
        Returns:
            String
        """

    url = url_list[0]
    print(url)
    image_location = url_list[1]
    rank = url_list[2]
    detected = False

    options = Options()
    options.headless = True

    browser_profile = webdriver.FirefoxProfile()
    browser_profile.set_preference("dom.webnotifications.enabled", False)

    try:
        driver = webdriver.Firefox(options=options, firefox_profile=browser_profile)
    except:
        sys.stdout.flush()
        print(str(rank) + " " + url + " failed_driver")
        return str(rank) + " " + url + " failed_driver"

    try:
        driver.get(url)
    except:
        sys.stdout.flush()
        print(str(rank) + " " + url + " " + " failed_url")
        driver.quit()
        return str(rank) + " " + url + " failed_url"

    driver.maximize_window()

    # changes all links open in new tabs

    if "403 Forbidden" in driver.page_source:
        error_403_url_list.append(url)
        sys.stdout.flush()
        print(str(rank) + " " + url + " Failed_403")
        driver.quit()
        return str(rank) + " " + url + " Failed_403"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    num_websites_to_crawl = 20
    start = time.time()
    print(start)
    with open(args.file, newline='\n') as csvfile:
        data = list(csv.reader(csvfile))
    urls_list = [("https://www." + url[1], "images_" + url[1] + "/", url[0]) for url in data]
    i=0
    print (len(urls_list))
    while i < len(urls_list):
        urls_list_subset = urls_list[i:i+num_websites_to_crawl]
        print(urls_list_subset)
        with multiprocessing.Pool(processes=10) as pool:
            processes = pool.map(main, urls_list_subset)
            pool.close()
            pool.join()
        for process in processes:
            with open('url_results.txt', 'a') as f:
                f.write(str(process) + "\n")
                f.close()
        i += num_websites_to_crawl
        print(processes)
    print(time.time() - start)