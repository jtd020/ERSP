from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import os
import shutil


def main(url, image_location, headless):
    if os.path.exists(image_location):
        shutil.rmtree(image_location)
    os.mkdir(image_location)

    options = Options()
    if headless:
        options.headless = True

    driver = webdriver.Firefox(options=options)
    driver.get(url)
    elements = driver.find_elements_by_tag_name("a")
    count = 0
    for element in elements:
        count += 1
        re_elements = driver.find_elements_by_tag_name("a")
        el = re_elements[elements.index(element)]
        location = el.location
        size = el.size

        try:
            before = take_screenshot(driver.get_screenshot_as_png(), location, size, "before" + str(count), image_location)
            # print("finished taking 'before' screenshot")
            # el.click()
            # driver.implicitly_wait(15)
            # driver.get(url)
            # print("finsihed going back")
            ActionChains(driver).key_down(Keys.CONTROL).click(el).key_up(Keys.CONTROL).perform()
            driver.implicitly_wait(10)
            driver.delete_all_cookies()
            driver.implicitly_wait(10)
            driver.refresh()
            driver.implicitly_wait(10)
            original_handle = driver.window_handles[0]
            for handle in driver.window_handles:
                if handle != original_handle:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.implicitly_wait(15)
            driver.switch_to.window(driver.window_handles[0])
            # print("finsihed going back")
        except:
            continue

        after = take_screenshot(driver.get_screenshot_as_png(), location, size, "after" + str(count), image_location)
        print("finished taking 'after' screenshot")

        if compare_images(before, after):
            break
        # os.remove(before)
        # os.remove(after)

    driver.close()
    # for handle in driver.window_handles:
    #     driver.switch_to.window(handle)
    #     driver.close()


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
        print("images are the same")
        return False
    else:
        cv2.imwrite("result.png", difference)
        cv2.imwrite("before.png", before_image)
        cv2.imwrite("after.png", after_image)
        print("images are different")
        print(after)
        return True


def element_href_test(url):
    driver = webdriver.Firefox()
    driver.get(url)
    elements = driver.find_elements_by_tag_name("a")
    for element in elements:
        print (element.get_attribute('href'))


if __name__ == "__main__":
    main("https://www.youtube.com", "images_youtube\\", False)
    # element_href_test("https://www.youtube.com")