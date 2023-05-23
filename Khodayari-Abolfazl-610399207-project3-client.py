from pyexpat import model
from requests import Session
from bs4 import BeautifulSoup
import re
import json
import socket
from typing import Union
import pandas as pd

def sendmessage(result_dict: dict) -> None:
    result_string = json.dumps(result_dict, default=str)
    result_string = f'{len(result_string):<{15}}' + result_string
    socket1.send(bytes(result_string, encoding='utf-8'))
    
def getmessage() -> Union[list, dict, str]:
    message_len1 = int(socket1.recv(15).decode('utf-8'))
    message1 = socket1.recv(message_len1)
    while len(message1) != message_len1:
        message1 += socket1.recv(message_len1)
    message1 = message1.decode('utf-8')
    return json.loads(message1)

port = 9881
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.connect(('localhost', port))
address_info = str(socket1.getpeername())
print("connected to server using: %s" % address_info)
sesion = Session()
request1 = sesion.post("http://utproject.ir/bp/login.php", data={"username": 610399207, "password":3971708956492952127})
if request1.status_code == 200:
    print('---Successfully logged in---')
    print()
j = 1
for i in range(500):
    result1 = sesion.get("http://utproject.ir/bp/Cars/page%s.php" %str(i))
    result1.encoding = 'utf8'
    if result1.status_code == 200:
        print('---Successfully get page %s ---' %str(i))
        print()
    soup1 = BeautifulSoup(result1.text, "html.parser",)
    cars = soup1.find_all(class_="car-list-item-li list-data-main")
    urlpattern = re.compile(r'(https://bama\.ir/car/detail-)([^-]+)-([^-]+)-([^-]+)-(.*)([0-9]{4})')
    for car in cars:
        url = str(car['data-url'])
        urlmatches = urlpattern.search(url)
        company = urlmatches.group(3)
        model = urlmatches.group(4)
        tream = "r"
        if urlmatches.group(5):
            tream = urlmatches.group(5)[:-1]
        year = urlmatches.group(6)
        car_details = car.select('div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1)')
        car_details = str(car_details)
        killometr_match = re.search(r'([0-9,]+)', car_details)
        killometr = '0'
        if killometr_match:
            killometr = re.sub(r',', '', killometr_match.group(0))
        price = car.select('div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > p:nth-child(1) > span:nth-child(1)')[0]['content']
        if price == 'IRR':
            price = '-1'
            if car.find_all(class_="cost installment-cost"):
                price = '-2'
        # carlist.append([company, model, tream, killometr, price, year])
        sendmessage(f'A{j} = {company}')
        sendmessage(f'B{j} = {model}')
        sendmessage(f'C{j} = {tream}')
        sendmessage(f'D{j} = {killometr}')
        sendmessage(f'E{j} = {price}')
        sendmessage(f'F{j} = {year}')
        j += 1
sendmessage('get result')
carlist = getmessage()[:j-1]
pd.set_option('display.max_columns', None)
cdf = pd.DataFrame(carlist, columns = ['company', 'model', 'tream', 'used', 'price', 'year'])
cdf[['used', 'year', 'price']] = cdf[['used', 'year', 'price']].astype(int)

print('Question 1:')
print(cdf[(cdf.company == 'hyundai') | (cdf.company == 'peugeot')].model.unique())
print('--- --- --- --- ---')

print('Question 2:')
print(len(cdf[(cdf.year > 2017) | ((cdf.year > 1395) & (cdf.year < 1401))].index))
print('--- --- --- --- ---')

print('Question 3:')
print(cdf[(cdf.company == 'peugeot') & (cdf.model == '206sd')].tream.unique())
print('Most frequent:', cdf[(cdf.company == 'peugeot') & (cdf.model == '206sd')].tream.value_counts().idxmax())
print('--- --- --- --- ---')

print('Question 4:')
cdf['age'] = 2023-cdf.year
cdf.loc[cdf['year'] < 1401, 'age'] = 1401-cdf.year
cdf['usedperyear'] = cdf.used // cdf.age
print(cdf[(cdf.usedperyear == cdf.usedperyear.max())])
cdf.drop(['usedperyear', 'age'], axis=1, inplace=True)
print('--- --- --- --- ---')

print('Question 5:')
avr_company = cdf[['company', 'price']][cdf.price>0].groupby(['company']).mean()
print(avr_company[avr_company.price == avr_company.price.max()])
print('--- --- --- --- ---')

print('Question 6:')
mostcar = cdf.model.value_counts().idxmax()
print(mostcar,' : ',len(cdf[(cdf.model == mostcar)].index), 'times')
print('--- --- --- --- ---')

print('Question 7:')
print(cdf[(cdf.company == 'peugeot') & (cdf.model == '206') & ((cdf.year > 1392) & (cdf.year < 1401)) & (cdf.price > 0)].price.mean()-
      cdf[(cdf.company == 'peugeot') & (cdf.model == '206') & ((cdf.year > 1384) & (cdf.year < 1393)) & (cdf.price > 0)].price.mean())
