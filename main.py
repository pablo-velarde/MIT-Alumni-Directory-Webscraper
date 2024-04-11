import time
import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv

username = ''
password = ''

main_url = 'https://alum.mit.edu/directory/#/directory-search-results'
company_name = input("Enter the company name: ")

session = webdriver.Edge()
session.get(main_url)

username_field = WebDriverWait(session, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
password_field = WebDriverWait(session, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
username_field.send_keys(username)
password_field.send_keys(password)
password_field.submit()

filter_arrow = WebDriverWait(session, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.select2-selection__arrow')))
filter_arrow.click()

company_filter = WebDriverWait(session, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/span/span/span[2]/ul/li[3]')))
company_filter.click()

search_bar = WebDriverWait(session, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div[1]/div/div[1]/div[1]/div/span[2]/input[2]')))
search_bar.send_keys(company_name)
search_bar.send_keys(Keys.RETURN)

time.sleep(2)

with open('mit_alumni_directory.csv', 'a', newline='') as csvfile:
    fieldnames = ['Company', 'Name', 'Job Title', 'Degree', 'Contact']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    html_content = session.page_source
    soup = BeautifulSoup(html_content, "lxml")
    directory_search_results = soup.find_all('div', class_ = 'directory-search-result')

    for result in directory_search_results:
        job_title = result.find('div', class_ = 'directory-search-result__job-title').text.strip()
        degree = result.find('div', class_ = 'directory-search-result__degree').text.strip()
        name = result.find('div', class_ = 'directory-search-result__name').text.strip()
        more_info = result.li.a["href"]
        client_url = "https://alum.mit.edu/directory/" + more_info.strip()

        session.get(client_url)
        contact_link_element = WebDriverWait(session, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="mailto:"]')))
        contact_link = contact_link_element.get_attribute('href')
        contact = contact_link.replace('mailto:', '')

        writer.writerow({ 'Company': company_name, 'Name': name, 'Job Title': job_title, 'Degree': degree, 'Contact': contact})

        session.execute_script("window.history.go(-1)")
        session.implicitly_wait(10)
    try:
        next_page_button = WebDriverWait(session, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div/div/div/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/ul[1]/li[8]/a')))
        next_page_button.click()
        time.sleep(2)
    except:
        print("Scraping Complete!")
