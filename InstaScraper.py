import cv2
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import  expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import os
import wget
import time

folderNames = []
keywords = []

def searchScraper(keywords):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Firefox()
    driver.get('https://www.instagram.com/accounts/login/')

    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username.clear()
    password.clear()

    username.send_keys("jrdnsgallery")
    password.send_keys("--instagram password--")

    logIn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
    try:
        not_now = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
        not_now.click()
        time.sleep(2)
    except:
        pass    
    
    time.sleep(5)
    
    searchbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
    searchbox.clear()

    for keyword in keywords:
        searchbox.send_keys(keyword)
        time.sleep(5)
        my_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/" + keyword[1:] + "/')]")))
        my_link.click()

        n_scrolls = 2
        for j in range(0, n_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

        anchors = driver.find_elements_by_tag_name('a')
        anchors = [a.get_attribute('href') for a in anchors]

        anchors = [a for a in anchors if str(a).startswith("https://www.instagram.com/p/")]

        print('Found ' + str(len(anchors)) + ' links to images')
        anchors[:5]

        images = []

        for a in anchors:
            driver.get(a)
            time.sleep(5)
            img = driver.find_elements_by_tag_name('img')
            img = [i.get_attribute('src') for i in img]
            images.append(img[1])
            
        images[:5]    
        folderNames = []

        path = os.getcwd()
        path = os.path.join(path, keyword[1:] + " images")

        os.mkdir(path)
        folderNames.append(str(keyword[1:] + " images"))

        counter = 0
        for image in images:
            save_as = os.path.join(path, keyword[1:] + str(counter) + '.jpg')
            wget.download(image, save_as)
            counter += 1

def getDescriptions(driver, targetInfluencer: str, num_posts: int):
    
    
    
    

def computerVisionSorter():
    cap = cv2.VideoCapture(0)
    prototxt_path = "weights/deploy.prototxt.txt"
    model_path = "weights/res10_300x300_ssd_iter_140000_fp16.caffemodel"

    model = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    
    counter = 0
    for keyword in keywords:
        image = cv2.imread(str(keyword[1:] + str(counter) + '.jpg'))
        counter += 1
        h, w = image.shape[:2]

        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))
        model.setInput(blob)
        output = np.squeeze(model.forward())

        font_scale = 1.0
        for i in range(0, output.shape[0]):
            confidence = output[i, 2]
            if confidence > 0.5:
                box = output[i, 3:7] * np.array([w, h, w, h])
                start_x, start_y, end_x, end_y = box.astype(np.int)
                cv2.rectangle(image, (start_x, start_y), (end_x, end_y), color=(255, 0, 0), thickness=2)
                cv2.putText(image, f"{confidence*100:.2f}%", (start_x, start_y-5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
                cv2.imwrite(str(keyword[1:] + str(counter) + '.jpg'), image)
