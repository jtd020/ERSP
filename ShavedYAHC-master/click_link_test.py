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
    if os.path.exists(image_location):
        shutil.rmtree(image_location)
    os.mkdir(image_location)

    options = Options()
    if headless:
        options.headless = True

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 3)
    driver.get(url)
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
            ActionChains(driver).key_down(Keys.CONTROL).double_click(el).key_up(Keys.CONTROL).send_keys(Keys.ESCAPE).perform()
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
    im = Image.open(BytesIO(image))

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))

    im.save(image_location + name + ".png")
    return str(image_location + name + ".png")


def compare_images(before, after):
    before_image = cv2.imread(before)
    after_image = cv2.imread(after)
    difference = cv2.subtract(after_image, before_image)
    result = not np.any(difference)

    if result:
        return False
    else:
        cv2.imwrite("result.png", difference)
        cv2.imwrite("before.png", before_image)
        cv2.imwrite("after.png", after_image)
        return True


if __name__ == "__main__":
    main("https://www.facebook.com", "images_facebook\\", False)
