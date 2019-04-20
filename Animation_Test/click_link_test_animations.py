from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO

import cv2
import numpy as np
import os
import shutil
import time


def main(url, image_location, headless):
    make_directory(image_location)

    options = Options()
    if headless:
        options.headless = True

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 3)
    driver.get(url)
    time.sleep(3)
    driver.maximize_window()

    # changes all links open in new tabs
    driver.execute_script("""
        var items = document.getElementsByTagName("a");
        Array.from(items).forEach(function(item){
        var attributes = Object.values(item.attributes);
        for (i=0; i < attributes.length; i++) {
            console.log(typeof attributes[i].nodeName.toString());
            if (attributes[i].nodeName.toString() != "href" && attributes[i].nodeName.toString() != "class") {
                item.removeAttribute(attributes[i].nodeName.toString());
            }
        }
        item.setAttribute("target", "_blank");
        var new_element = item.cloneNode(true);
        item.parentNode.replaceChild(new_element, item); 
        item.addEventListener("click", function(event){
            event.stopPropagation();
            event.preventDefault();
            return false;
        });
    });""")

    # removes animated elements on page
    three_minutes = 60 * 3
    remove_animations(driver, three_minutes)
    print("done removing animations")
    return

    elements = driver.find_elements_by_tag_name("a")
    count = 0

    for element in elements:
        count += 1

        try:
            el = element
            location = el.location
            size = el.size
            ActionChains(driver).move_to_element(el).perform()
            before = take_screenshot(driver.get_screenshot_as_png(), location, size, "before" + str(count), image_location)
            wait.until(EC.visibility_of(el))

            # clicks on link
            ActionChains(driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[0])
            driver.implicitly_wait(10)
            driver.delete_all_cookies()
            driver.implicitly_wait(10)

            original_handle = driver.window_handles[0]
            # deletes all uncessary tabs
            for handle in driver.window_handles:
                if handle != original_handle:
                    driver.switch_to.window(handle)
                    driver.close()

            ActionChains(driver).move_to_element(el)
            driver.switch_to.window(driver.window_handles[0])

        except:
            original_handle = driver.window_handles[0]

            for handle in driver.window_handles:
                if handle != original_handle:
                    driver.switch_to.window(handle)
                    driver.close()

            driver.implicitly_wait(15)
            driver.switch_to.window(driver.window_handles[0])
            continue

        after = take_screenshot(driver.get_screenshot_as_png(), location, size, "after" + str(count), image_location)

        if compare_images(before, after):
            print("Feature detected")
            break
        os.remove(before)
        os.remove(after)

    shutil.rmtree(image_location)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        driver.close()


def take_screenshot(image, location, size, name, image_location):
    print('taking a screen shot')
    im = Image.open(BytesIO(image))

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    #im = im.crop((left, top, 2*right, 2*bottom))

    im.save(image_location + name + ".png")
    return str(image_location + name + ".png")

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

def compare_images(before, after):
    before_image = cv2.imread(before)
    after_image = cv2.imread(after)
    difference = cv2.subtract(after_image, before_image)
    result = not np.any(difference)

    if result:
        return False
    else:
        make_directory("image_comparison/")
        cv2.imwrite("image_comparison/result.png", difference)
        cv2.imwrite("image_comparison/before.png", before_image)
        cv2.imwrite("image_comparison/after.png", after_image)
        return True

def remove_animations(driver, timeout):
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
    while timeout > curr_sec - prev_sec and no_animation_count < count_timeout:
        if animation_detected(driver):
            print("animation detected")
            remove_animated_element(driver)
            no_animation_count = 0

        curr_sec = time.time()
        no_animation_count += 1
        print("no animation count: " + str(no_animation_count))


def animation_detected(driver):
    """ 
    Description:
        Removes animated objects on website using image differencing. 
    Args:
        driver:  Firefox browser.
    Returns:
        True if the before and after screenshot are different, False otherwise.
    """
    make_directory("animation/")
    location = {'x': 0, 'y': 0}
    window_size = driver.get_window_size()
    before = take_screenshot(driver.get_screenshot_as_png(), location, window_size, "animation_before", "animation/")
    time.sleep(1)
    after  = take_screenshot(driver.get_screenshot_as_png(), location, window_size, "animation_after", "animation/")
    return compare_images(before, after)

def remove_animated_element(driver):
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
    if not os.path.exists("image_comparison/result.png"):
        return

    resize_image("image_comparison/result.png", driver.get_window_size())
    im = Image.open("image_comparison/result.png")
    width = im.size[0]
    height = im.size[1]
    pixel = im.load()

    #skip (0,0) because of non-visible elements like scripts.
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
    print("at (" + str(x) + ", " + str(y)+ ")")
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


def make_directory(image_location):
    if os.path.exists(image_location):
        shutil.rmtree(image_location)
    os.mkdir(image_location)

if __name__ == "__main__":
    #main("https://www.facebook.com", "images_facebook/", False)
    #main("https://www.cnn.com/", "images_cnn/", False)
    main("https://www.leaflabs.com/", "images_leaflabs/", False)
    main("https://www.bluecompass.com/", "images_blue/", False)
    #main("https://www.youtube.com/", "images_leaflabs/", False)
    main("https://www.javascript-fx.com/submitscripts/fireworks/", "images_fireworks/", False)

