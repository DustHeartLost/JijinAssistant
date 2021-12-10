import requests
import json
import time
import re
import json
from bs4 import BeautifulSoup


class Funds:
    """基金处理类,主要功能包括：
        1.获取基金相关信息
        2.筛选符合条件的基金信息
    """

    def __init__(self) -> None:
        """初始化得到所有基金的基本数据
        """
        url = 'http://fund.eastmoney.com/data/FundGuideapi.aspx?dt=4&sd=&ed=&sc=3y&st=desc&pi=1&pn=10000&zf=diy&sh=list&rnd=0.24506401305749903'
        response = requests.get(url)
        self.fundsList = json.loads(response.text.split('=')[1])['datas']

        # 将数据截取，只留下基金代码和基金名称
        for i in range(len(self.fundsList)):
            temp = self.fundsList[i].split(',')
            self.fundsList[i] = temp[0]+'-'+temp[1]

    def findFundManager(self, fundCode):
        """获取基金经理的基本信息

        Args:
            fundCode (String): 基金代码

        Returns:
            String: 基金经理基本信息的Json字符串
        """
        v = time.strftime(r'%Y%m%d%H%M%S')
        url = f"http://fund.eastmoney.com/pingzhongdata/{fundCode}.js?v={v}"
        fundData = requests.get(url).text
        # 现任基金经理的基本信息，可能存在多个基金经理，所以返回值是一个Jsonlist
        Data_currentFundManager = json.loads(re.findall(
            r"var Data_currentFundManager =([^;]*)", fundData, 0)[0])
        return Data_currentFundManager

    def findFundInformation(self,fundCode):
        """根据基金代码返回基金的基本信息

        Args:
            fundCode (String): 基金代码

        Returns:
            Json: 基金基本信息的json字符串
        """
        Data_fundInformation = {}
        url = f"http://fundf10.eastmoney.com/jbgk_{fundCode}.html"
        html = requests.get(url).text
        table = BeautifulSoup(html, "html.parser").find(
            "table", attrs={"class": "info w790"})
        trs = table.find_all("tr")[1:]
        for tr in trs:
            ths = tr.find_all("th")
            tds = tr.find_all("td")
            for i in range(len(ths)):
                Data_fundInformation[ths[i].text] = tds[i].text
        return Data_fundInformation


if __name__ == "__main__":
    # TODO: 完善后续的各个字段的取值
    fundCode = "001595"
    v = time.strftime(r'%Y%m%d%H%M%S')
    fund = Funds()
    print(fund.findFundManager(fundCode))
