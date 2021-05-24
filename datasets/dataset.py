from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from sklearn.feature_extraction.text import TfidfVectorizer
from utils.utils import calculate_true_relationship
import os
import numpy as np
import pandas as pd

GECKO_PATH = "drivers/geckodriver"
binary = FirefoxBinary('/usr/bin/firefox')
ADBLOCK_PATH = "drivers/adblock_plus-3.10-an fx.xpi"


def modify_link_s1():
    new_file = open("datasets/new_s1.txt", "a")
    firefox = webdriver.Firefox(firefox_binary=binary, executable_path=GECKO_PATH)
    with open("datasets/s1.txt") as f:
        links = f.read().splitlines()
        for link in links:
            firefox.get(link)
            value = firefox.current_url
            new_file.write(value)
            new_file.write("\n")
            firefox.back()
    new_file.close()
    os.remove("datasets/s1.txt")
    os.rename("datasets/new_s1.txt", "datasets/s1.txt")


def get_link_player(links, name):
    f = open("datasets/" + name + ".txt", "a")
    for link in links:
        value = link.get_attribute("href")
        f.write(value)
        f.write("\n")
    f.close()
    if name == "s1":
        modify_link_s1()


def get_s1():
    if not os.path.isfile("datasets/s1.txt"):
        firefox = webdriver.Firefox(firefox_binary=binary, executable_path=GECKO_PATH)
        firefox.get("https://www.rotoworld.com/basketball/nba/teams")

        if os.path.isfile('datasets/s1_squadre.txt'):
            print("File con link a squadre rotoworld trovato")
        else:
            f = open("datasets/s1_squadre.txt", "a")
            squadre = firefox.find_elements_by_xpath("//*[@class='team-listing-banner__wrap']")
            for squadra in squadre:
                f.write(squadra.get_attribute("href"))
                f.write("\n")
            f.close()

        with open("datasets/s1_squadre.txt") as f:
            lines = f.read().splitlines()
            for line in lines:
                firefox.get(line)
                links = firefox.find_elements_by_xpath(
                    "//table[@class='stats-table table-scroll__table team-stats-per-game']/tbody/tr/td/a")
                get_link_player(links, "s1")

    ''' ELIMINAZIONE DI DUPLICATI '''

    with open("datasets/s1.txt") as f:
        set_s1 = f.read().splitlines()
    f = open("datasets/s1.txt", "w")
    if len(set_s1) != 0:
        for line in list(dict.fromkeys(set_s1)):
            f.write(line)
            f.write("\n")
    f.close()

    with open("datasets/s1.txt") as f:
        return f.read().splitlines()


def get_s2():
    if not os.path.isfile("datasets/s2.txt"):
        firefox = webdriver.Firefox(firefox_binary=binary, executable_path=GECKO_PATH)
        firefox.get("https://www.nba.com/players")
        WebDriverWait(firefox, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                     "//select[@title = 'Page Number Selection Drown Down List' and @class = 'DropDown_select__5Rjt0']"))).click()
        WebDriverWait(firefox, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                     "//select[@title = 'Page Number Selection Drown Down List' and @class = 'DropDown_select__5Rjt0']/option[@value='-1']"))).click()

        links = firefox.find_elements_by_xpath("//a[@class='flex items-center t6']")
        get_link_player(links, "s2")

    with open("datasets/s2.txt") as f:
        return (f.read().splitlines())

    ''' ELIMINAZIONE DI DUPLICATI '''

    with open("datasets/s2.txt") as f:
        set_s2 = f.read().splitlines()
    f = open("datasets/s2.txt", "w")
    if len(set_s2) != 0:
        for line in list(dict.fromkeys(set_s2)):
            f.write(line)
            f.write("\n")
    f.close()
    with open("datasets/s2.txt") as f:
        return f.read().splitlines()


def get_s3():
    if not os.path.isfile("datasets/s3.txt"):
        firefox = webdriver.Firefox(firefox_binary=binary, executable_path=GECKO_PATH)
        firefox.get("https://basketball.realgm.com/nba/players")
        links = firefox.find_elements_by_xpath("//*[@class='nowrap tablesaw-cell-persist' and @data-th='Player']/a")
        get_link_player(links, "s3")

    ''' ELIMINAZIONE DI DUPLICATI '''

    with open("datasets/s3.txt") as f:
        set_s3 = f.read().splitlines()
    f = open("datasets/s3.txt", "w")
    if len(set_s3) != 0:
        for line in list(dict.fromkeys(set_s3)):
            f.write(line)
            f.write("\n")
    f.close()
    with open("datasets/s3.txt") as f:
        return f.read().splitlines()


def to_dataframe(name):

    s1 = get_s1()
    s2 = get_s2()
    s3 = get_s3()

    dataset = {
        "s1": s1,
        "s2": s2,
        "s3": s3
    }


    ffprofile = webdriver.FirefoxProfile()
    ffprofile.add_extension(ADBLOCK_PATH)
    ffprofile.set_preference("extensions.adblockplus.currentVersion", "3.10")
    #binary = FirefoxBinary('/usr/bin/firefox')
    firefox = webdriver.Firefox(firefox_profile=ffprofile, firefox_binary=binary, executable_path=GECKO_PATH)

    for k in dataset.keys():
        rows = []
        if os.path.isfile("checkpoints/rows_" + k + ".pkl"):
            rows = pd.read_pickle(r'checkpoints/rows_' + k + '.pkl')
        print(rows)
        print("start, rows_{} length {}".format(k,len(rows)))
        s = dataset.get(k)
        for p in range(len(rows), len(s)):
            #print(s[p])
            firefox.get(s[p])
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
            #titolo = WebDriverWait(firefox, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH, "//'title'")))
            '''
            if k == "s1" :
                leaves = firefox.find_elements_by_xpath("//div[@class='content content--main cols-8']")
            elif k == "s2" :
                leaves = firefox.find_elements_by_xpath("//div[@class='flex flex-col bg-teams-MIL']")
            else :
                leaves = firefox.find_elements_by_xpath("//div[@class='wrapper clearfix container']")
            row_page = ""
            for leaf in leaves:
                try:
                    #rows.append(" " + leaf.text)
                    row_page += " " + leaf.text
                except StaleElementReferenceException:
                    print("ECCEZIONE")
            row_page += "\n"
            #print(row_page)
            rows.append(row_page)
            '''
            titolo = WebDriverWait(firefox, 10, ignored_exceptions=ignored_exceptions).until(lambda s: s.find_element(By.XPATH, "//head/title"))
            #WebDriverWait(firefox, 10, ignored_exceptions=ignored_exceptions)#.until(EC.presence_of_all_elements_located((By.XPATH, "//head/title")))
            #titolo = firefox.find_element_by_xpath("//head/title")
            t = titolo.get_attribute("text").replace("-"," ").replace("|"," ").replace(","," ").replace("."," ").replace("/"," ")
            rows.append(t)
            if len(rows) % 10 == 0 or len(rows) == len(s) or len(rows) == 1:
                pd.to_pickle(rows, "checkpoints/rows_" + k + ".pkl")
                print("save checkpoint, rows_{} length {}".format(k, len(rows)))
                #print(rows)

    firefox.close()
    name_sx = name.rsplit('_')[0]
    name_dx = name.rsplit('_')[1]

    rows_sx = pd.read_pickle(r'checkpoints/rows_' + name_sx + '.pkl')
    rows_dx = pd.read_pickle(r'checkpoints/rows_' + name_dx + '.pkl')

    for i in range(len(rows_sx)):
        rows_sx[i] = rows_sx[i].lower()

    for i in range(len(rows_dx)):
        rows_dx[i] = rows_dx[i].lower()

    print(rows_sx)

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors_sx = vectorizer.fit_transform(rows_sx)
    vectors_dx = vectorizer.transform(rows_dx)

    feature_names = vectorizer.get_feature_names()
    dense_sx = vectors_sx.todense()
    denselist_sx = dense_sx.tolist()

    dense_dx = vectors_dx.todense()
    denselist_dx = dense_dx.tolist()

    denselist = np.concatenate((denselist_sx, denselist_dx))
    df = pd.DataFrame(denselist, columns=feature_names)
    df.to_csv("dataframes/df_" + name + ".csv", index=False)

    if not os.path.isfile("true_relationship/true_relationship_s1_s2.txt"):
        calculate_true_relationship(s1, s2, "s1_s2")
    if not os.path.isfile("true_relationship/true_relationship_s1_s3.txt"):
        calculate_true_relationship(s1, s3, "s1_s3")
    if not os.path.isfile("true_relationship/true_relationship_s2_s3.txt"):
        calculate_true_relationship(s2, s3, "s2_s3")
