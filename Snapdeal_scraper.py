
#IMPORTING NECESSARY LIBRARIES

from selenium import webdriver
from bs4 import BeautifulSoup
import time, json
from tabulate import tabulate
import requests
import mysql.connector
from datetime import date

#FUNCTION TO PARSE EACH PRODUCT AND FETCH THE DETAILS


def snapdealparser(url,category):
    #time.sleep(1)

    '''headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    '''
    response = requests.get(url)#, headers=headers)

    output = []

    htmltext = response.text
    soup = BeautifulSoup(htmltext, 'html.parser') #parsing

    name = soup.findAll('img', {'class': "cloudzoom"})[0].get('title')

    price = soup.find('span', {'class': "payBlkBig"})

    rating = soup.find('span', {'class': "avrg-rating"})

    photo = soup.findAll('img', {'class': "cloudzoom"})[0].get('src')

    rating_count=soup.find('span',{'class': "total-rating showRatingTooltip"})




    link = url
    if name:
        output.append(name)
    else:
        output.append(None)

    if price:
        price=price.text
        if ',' in price:
            price=int(price.replace(',',''))
            output.append(price)
        else:
            output.append(int(price))
    else:
        output.append(None)

    if rating:
        output.append(rating.text)
    else:
        output.append(None)
    if rating_count:
        output.append(rating_count.text)
    else:
        output.append(0)
    if photo:
        output.append(photo)
    else:
        output.append(None)
    output.append(link)

    store_in_db(output,category)

    return #output

#FUNCTION TO FETCH LINK OF EACH PRODUCTS WITH GIVEN NUMBER OF COUNTS

def get_links():

    print("Enter the category to be searched\n")
    query = input()

    prod_count=int(input('Enter the number of products you want to fetch\n'))

    driver = webdriver.Chrome(executable_path=r"C:\\Users\\Acer\\Downloads\\chromedriver_win32\\chromedriver.exe")

    url = 'https://www.snapdeal.com/search?keyword='+query.lower()+'&santizedKeyword=&catId=&categoryId=0&suggested=true&vertical=&noOfResults=20&searchState=&clickSrc=suggested&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=&url=&utmContent=&dealDetail=&sort=plrty'
    driver.get(url)
    time.sleep(1)

    ulen, llen = 0, 0
    while True:
        for scroll in range(1):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        main_div = soup.find("div", {"id": "products"})
        page = main_div.find_all("div", {"class": "col-xs-24"})
        #print(len(page))

        for i in page:
            div = i.find("div", {"id": "pagination-txt"})
            ulen = int(div.find("span", {"id": "pagination-upper-count"}).text)
            #llen = int(div.find("span", {"id": "pagination-lower-count"}).text)
        #print(ulen)
        if ulen >= prod_count:
            break
        else:
            pass

    driver.quit()

    section = main_div.find_all("section", {"data-dpwlbl": "Product Grid"})
    links = []
    for x, i in enumerate(section):
        in_div = i.find_all("div", {"class": ["col-xs-6  favDp product-tuple-listing js-tuple", "product-hover-state"]})
        for y, j in enumerate(in_div):
            a = j.find("a", {"target": "_blank"})
            links.append(a.get("href"))
    print("total products found: ",len(links))
    return (links,query)

def get_data():
    links,category=get_links()
    #extracted_data = []

    for i in links:

        snapdealparser(i,category)
        #time.sleep(1)



def print_data(extracted_data):
    print(tabulate(extracted_data, headers=["Product", "Price", "Rating", "Rating Count", "Image", "URL"],
                   tablefmt="fancy_grid"))
def store_in_db(output,category):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="aman@mysql",
        database="mirraw")

    mycursor = mydb.cursor()
    ins="INSERT INTO scrapped_data (name,category,offerd_price,rating,avg_rating,url,source,date) VALUES (%s,%s,%s, %s,%s,%s,%s,%s)"
    val=(output[0],category,output[1],output[2],output[3],output[5],'snapdeal',date.today())
    mycursor.execute(ins,val)

    ins_image = "INSERT INTO image (url,image) VALUES (%s,%s)"
    val2=(output[5],output[4])
    mycursor.execute(ins_image,val2)
    mydb.commit()
    return




if __name__ == "__main__":
    get_data()