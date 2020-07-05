import requests
from bs4 import BeautifulSoup
import insert_to_db as db
import re
import pandas as pd
from tabulate import tabulate
import sys
from sqlalchemy import create_engine
import json


product_name=pd.DataFrame(columns=['id','p_name','p_days','p_price','p_source'])
date_seat=pd.DataFrame(columns=['p_id','p_date','p_seat','p_available','flight_go','flight_back'])
flight=pd.DataFrame(columns=['id','airline','departPort','departTime','arrivePort','arriveTime'])

param={
    'displayType':'G',
	'subCd':'',
	'orderCd': '1',
	'pageALL': 1,
	'pageGO': '1',
	'pageGI': '',
	'pagePGO': '1',
	'waitData': 'false',
	'waitPage': 'false',
	'mGrupCd': '',
	'SrcCls': 'D',
	'tabList': '',
	'regmCd':'', 
	'regsCd':'', 
	'beginDt': '2020/07/03',
	'endDt': '2021/07/03',
	'portCd': '',
	'tdays':'', 
	'bjt':'', 
	'carr':'', 
	'allowJoin': '1',
	'allowWait': '1',
	'ikeyword': ''
}
count=1
res=requests.post('https://www.newamazing.com.tw/EW/Services/SearchListData.asp', data=param)
data=json.loads(res.text)['All']



while data and count<=5:
	# print(data[])

	for item in data:

		# store info
		id=item['GrupCd'][:7]+item['GrupCd'][-1:]
		name=item['GrupSnm']
		date=item['LeavDt']
		days=item['GrupLn']
		price=item['SaleAm']
		total=item['EstmYqt']
		available=item['DoneYqt']
		url='https://www.newamazing.com.tw/EW/Services/SearchFlight.asp?prodCd='+item['GrupCd']+'&sacctNo=&flightType=1'
		source='newamazing'

		#check flight
		flight_detail=requests.get(url)
		flight_info=json.loads(flight_detail.text)['Flights']
		# print(flight_info)
		
		go_back=[None,None]
		if flight_info:
			i=0
			for f in flight_info[:2]:
				fid=f['FltNo']+f['DepDt'][5:7]+f['DepDt'][8:]+f['DepCityNm']
				
				# store go and back flight 
				go_back[i]=fid
				i+=1
				
				if fid not in flight.values:
					flight=flight.append({
						'Id':fid,
						'airline':f['CarrNm'],
						'departCity':f['DepCityNm'],
						'departPort':f['DepAirpNm'],
						'departDate':f['DepDt'],
						'departTime':f['DepTm'],
						'arriveCity':f['ArrCityNm'],
						'arrivePort':f['ArrAirpNm'],
						'arriveDate':f['ArrDt'],
						'arriveTime':f['ArrTm']
						},ignore_index=True)
				
		flight=flight.dropna(axis='columns')
		

		if id not in product_name.values:
		    product_name=product_name.append({
		        'id':id,
		        'p_name': name,
		        'p_days': days,
		        'p_price': price,
		        'p_source':'newamazing'
		        }, ignore_index=True)
		    product_name=product_name.dropna(axis='columns')
		print(go_back[0])
		date_seat=date_seat.append({
			'p_id':id,
			'p_date':date,
			'p_seat':total,
			'p_available':available,
			'flight_go':go_back[0],
			'flight_back':go_back[1]
			},ignore_index=True)

	
	count+=1
	param['pageALL']=count
	res=requests.post('https://www.newamazing.com.tw/EW/Services/SearchListData.asp', data=param)
	data=json.loads(res.text)['All']


# print(tabulate(product_name,headers=['id','p_name','p_days','p_price','p_source','country'],tablefmt='grid'))
print(tabulate(date_seat,headers=['p_id','date','seat','available','flightId_go','flightId_back'],tablefmt='grid'))
# print(tabulate(flight,headers=['id','airline','departPort','departTime','arrivePort','arriveTime'],tablefmt='grid'))

# db.to_db('product',product_name)
# db.to_db('flight',flight)
db.to_db('date_seat',date_seat)
