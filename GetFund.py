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
        for temp in Data_currentFundManager:
            temp.pop("pic")
        return Data_currentFundManager

    def findFundInformation(self, fundCode):
        """根据基金代码返回基金的基本信息

        Args:
            fundCode (String): 基金代码

        Returns:
            Dictionary: 基金基本信息的字典对象
        """
        Data_fundInformation = {}
        tempData = {}
        url = f"http://fundf10.eastmoney.com/jbgk_{fundCode}.html"
        html = requests.get(url).text
        table = BeautifulSoup(html, "html.parser").find(
            "table", attrs={"class": "info w790"})
        trs = table.find_all("tr")
        for tr in trs:
            ths = tr.find_all("th")
            tds = tr.find_all("td")
            for i in range(len(ths)):
                tempData[ths[i].text] = tds[i].text
        targetThs = ["fundName", "fundCode", "fundType", "issueDate", "scale",
                     "fundCompany", "fundManager", "managementRate", "escrowRate", "salesRate", "index"]
        # ths = ["基金名称","基金代码","基金类型", "发行日期", "资产规模",
        #             "基金公司",    "基金经理",      "管理费率",      "托管费率",   "销售服务费","跟踪指数"]
        ths = ["基金简称", "基金代码", "基金类型", "发行日期", "资产规模", "基金管理人",
               "基金经理人",   "管理费率",      "托管费率",  "销售服务费率", "跟踪标的"]
        for i in range(len(targetThs)):
            Data_fundInformation[targetThs[i]] = tempData[ths[i]]
        Data_fundInformation["fundCode"] = Data_fundInformation["fundCode"][0:6]
        Data_fundInformation["scale"] = re.findall(
            r"(.*)份额规模", Data_fundInformation["scale"], 0)[0]
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
        theads = ["num", "code", "name", "proportion"]
        # theads = ["序号", "股票代码", "股票名称", "占净值比例"]
        for i in range(1, len(trs)):
            # 删除数据里不需要的元素
            tds = trs[i].find_all("td")
            del tds[3]
            del tds[3]
            del tds[3]
            del tds[4]
            del tds[4]
            tempData = {}
            for j in range(len(tds)):
                tempData[theads[j]] = tds[j].text
            Data_heavyStock.append(tempData)
        return Data_heavyStock

    def findFundHeavyBonds(self, fundCode):
        """根据基金代码查找基金的重仓债券

        Args:
            fundCode (String): 基金代码

        Returns:
            List: 重仓债券信息的字典对象列表
        """
        url = f'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=zqcc&code={fundCode}&topline=20'
        fundData = requests.get(url).text
        html = re.findall(r"content:\"(.*)\",arryear", fundData, 0)[0]
        table = BeautifulSoup(html, "html.parser").find(
            "table", attrs={"class": "w782 comm tzxq"})
        trs = table.find_all("tr")
        Data_heavyBonds = []
        theads = ["num", "code", "name", "proportion"]
        # theads = ["序号", "债券代码", "债券名称", "占净值比例"]
        for i in range(1, len(trs)):
            tds = trs[i].find_all("td")
            tempData = {}
            for j in range(len(tds)-1):
                tempData[theads[j]] = tds[j].text
            Data_heavyBonds.append(tempData)
        return Data_heavyBonds

    def isDuplicationInHeavy(self, fundCodes, way=1):
        """根据基金代码序列，查找基金直接持仓是否有重叠

        Args:
            fundCodes (List)): 基金代码列表
            way (int, optional): 若基金重仓是股票，way为1，若基金重仓是债券，way为2. Defaults to 1.

        Returns:
            [String]: 若有重叠返回重叠具体信息，否则返回False
        """
        Data = {}
        for code in fundCodes:
            Data[code] = self.findFundHeavyStock if way == 1 else self.findFundHeavyBonds(
                code)
        msg = ""
        for i in range(len(fundCodes)):
            for j in range(i+1, len(fundCodes)):
                temp = self.isDuplicationInlist(
                    Data[fundCodes[i]], Data[fundCodes[j]])
                if temp:
                    msg = msg+f"{fundCodes[i]},{fundCodes[j]}: "+temp+"\n"

        return msg if msg != "" else False

    def isDuplicationInlist(self, list1, list2):
        """根据给定的两个列表，判断第一个列表的内容是否出现在第二个列表中

        Args:
            list1 (List): 第一个列表
            list2 (List): 第二个列表

        Returns:
            [String]: 若第一个列表内容出现在第二个列表中，则返回具体内容，否则返回False
        """
        msg = ""
        for templist1 in list1:
            for templist2 in list2:
                if templist1["code"] == templist2["code"]:
                    msg = msg+templist1["name"]
        return False if msg == "" else msg


if __name__ == "__main__":
    # TODO: 完善后续的各个字段的取值
    fundCode = "000033"
    v = time.strftime(r'%Y%m%d%H%M%S')
    fund = Funds()
    print(fund.isDuplicationInHeavy(fundCodes=["161120", "000033"], way=2))
    # print(fund.findFundInformation(fundCode))
    # print(fund.findFundHeavyStock(fundCode))
    # print(fund.findFundHeavyBonds(fundCode))
