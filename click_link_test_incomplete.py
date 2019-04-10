from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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

    # caps = DesiredCapabilities().FIREFOX
    # caps["pageLoadStrategy"] = "none"
    # driver = webdriver.Firefox(desired_capabilities=caps, options=options)

    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # with open('r.js', 'r') as requirejs_js:
    #     # requirejs = requirejs_js.read()
    #     driver.execute_script(requirejs_js)

    with open('jquery-3.3.1.min.js', 'r') as jquery_js:
        jquery = jquery_js.read()
        driver.execute_script(jquery)

    # script = """require(['jquery'], function($) {""" \
    #                         """$(function(){""" \
    #                             """$.fx.off = true;""" \
    #                             """var styleEl = document.createElement('style');""" \
    #                             """styleEl.textContent = '*{ transition: none !important; transition-property: none !important; }';""" \
    #                             """document.head.appendChild(styleEl);""" \
    #                         """});""" \
    #                     """});""";
    # driver.execute_script(script)

    elements = driver.find_elements_by_tag_name("a")
    count = 0
    # print (len(elements))

    for element in elements:
        count += 1
        # driver.get(url)
        # driver.implicitly_wait(10)
        # re_elements = driver.find_elements_by_tag_name("a")
        # print (str(len(re_elements)) + " size")

        try:
            el = element
            location = el.location
            size = el.size
            ActionChains(driver).move_to_element(el).perform()
            before = take_screenshot(driver.get_screenshot_as_png(), location, size, "before" + str(count), image_location)

            # print("finished taking 'before' screenshot")
            # el.click()
            # driver.implicitly_wait(15)
            # driver.get(url)
            # print("finsihed going back")
            # ActionChains(driver).context_click(el).send_keys(Keys.ARROW_RIGHT).send_keys(Keys.RETURN).perform()
            # el.middle_click()
            # driver.execute_script("""
            #     var mouseWheelClick = new MouseEvent( "click", { "button": 1, "which": 1 });
            #     arguments[0].dispatchEvent(mouseWheelClick)""", el)

            # something = driver.execute_script("""
            #         var list = document.getElementsByTagName("A");
            #         var element = list[""" + str(elements.index(element)) + """];
            #         var e = element.ownerDocument.createEvent('MouseEvents');
            #         e.initMouseEvent("click", { "button": 1, "which": 1 });
            #         list[""" + str(elements.index(element)) + """].click();
            #     """)

            # ActionChains(driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).perform()

            ActionChains(driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).send_keys(Keys.ESCAPE).perform()

            driver.switch_to.window(driver.window_handles[0])
            driver.implicitly_wait(10)
            driver.delete_all_cookies()
            driver.implicitly_wait(10)

            original_handle = driver.window_handles[0]
            print (len(driver.window_handles))

            for handle in driver.window_handles:
                if handle != original_handle:
                    driver.switch_to.window(handle)
                    driver.close()

            ActionChains(driver).move_to_element(el)
            driver.switch_to.window(driver.window_handles[0])

        except:
            # print ("there was an error")
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
    # with BytesIO() as f:
    #     im.save(f, format='PNG')
    #     return f.getvalue()


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
        print("images are different")
        # print(after)
        return True


# def element_href_test(url):
#     driver = webdriver.Firefox()
#     driver.get(url)
#     elements = driver.find_elements_by_tag_name("a")
#     for element in elements:
#         print (element.get_attribute('href'))

if __name__ == "__main__":
    main("https://www.youtube.com", "images_youtube\\", False)
