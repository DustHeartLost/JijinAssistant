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
            Dictionary: 基金经理基本信息的字典对象
        """
        v = time.strftime(r'%Y%m%d%H%M%S')
        url = f"http://fund.eastmoney.com/pingzhongdata/{fundCode}.js?v={v}"
        fundData = requests.get(url).text
        # 现任基金经理的基本信息，可能存在多个基金经理，所以返回值是一个Jsonlist
        Data_currentFundManager = json.loads(re.findall(
            r"var Data_currentFundManager =([^;]*)", fundData, 0)[0])
        return Data_currentFundManager

    def findFundInformation(self, fundCode):
        """根据基金代码返回基金的基本信息

        Args:
            fundCode (String): 基金代码

        Returns:
            Dictionary: 基金基本信息的字典对象
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

    def findFundHeavyStock(self, fundCode):
        """根据基金代码查找基金的重仓股票

        Args:
            fundCode (String): 基金代码

        Returns:
            List: 重仓股票信息的字典对象列表
        """
        url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={fundCode}&topline=20"

        fundData = requests.get(url).text
        html = re.findall(r"content:\"(.*)\",arryear", fundData, 0)[0]
        table = BeautifulSoup(html, "html.parser").find(
            "table", attrs={"class": "w782 comm tzxq"})
        trs = table.find_all("tr")
        Data_heavyStock = []
        # 删除标题栏数组里不需要的元素
        theads = trs[0].find_all("th")
        del theads[3]
        del theads[3]
        del theads[3]
        del theads[4]
        del theads[4]
        for i in range(1,len(trs)):
            #删除数据里不需要的元素 
            tds = trs[i].find_all("td")
            del tds[3]
            del tds[3]
            del tds[3]
            del tds[4]
            del tds[4]
            tempData={}
            for j in range(len(tds)):
                tempData[theads[j].text] = tds[j].text
            Data_heavyStock.append(tempData)
        return Data_heavyStock


if __name__ == "__main__":
    # TODO: 完善后续的各个字段的取值
    fundCode = "001595"
    v = time.strftime(r'%Y%m%d%H%M%S')
    fund = Funds()
    print(fund.findFundHeavyStock(fundCode))
