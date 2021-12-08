import requests
import json

url1='http://fund.eastmoney.com/data/FundGuideapi.aspx?dt=4&sd=&ed=&sc=3y&st=desc&pi=1&pn=2000000&zf=diy&sh=list&rnd=0.24506401305749903'
# url = "https://fundgz.1234567.com.cn/js/217011.js"
response=requests.get(url1)
text = response.text.split('=')[1]
data=json.loads(text)
list=data['datas']
print(len(list))
# print(len(list[0].split(','))/24)
