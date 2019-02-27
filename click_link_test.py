from selenium import webdriver
from selenium.webdriver.firefox.options import Options
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
    print(len(elements))
    count = 0
    for element in elements:
        count += 1
        re_elements = driver.find_elements_by_tag_name("a")
        el = re_elements[elements.index(element)]
        location = el.location
        size = el.size

        try:
            before = take_screenshot(driver.get_screenshot_as_png(), location, size, "before" + str(count), image_location)
            print("finished taking 'before' screenshot")
            el.click()
            driver.implicitly_wait(15)
            driver.get(url)
            print("finsihed going back")
        except:
            continue

        after = take_screenshot(driver.get_screenshot_as_png(), location, size, "after" + str(count), image_location)
        print("finished taking 'after' screenshot")

        if compare_images(before, after):
            break

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
        print("images are the same")
        return False
    else:
        cv2.imwrite("result.png", difference)
        print("images are different")
        print(after)
        return True


if __name__ == "__main__":
    main("https://www.facebook.com/", "images_facebook\\", True)