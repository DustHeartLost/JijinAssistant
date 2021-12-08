import requests
import json
import time
import re
import json


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

    def findFund(fundCode):
        """获取单个基金的基本信息（天天基金网）,并通过正则表达式将其转为可识别的数据

        Args:
            fundCode (String): 基金代码

        Returns:
            String: 基金基本信息的Json字符串
        """
        v = time.strftime(r'%Y%m%d%H%M%S')
        url = f"http://fund.eastmoney.com/pingzhongdata/{fundCode}.js?v={v}"

        response = requests.get(url)
        return response.text


if __name__ == "__main__":
    # TODO: 完善后续的各个字段的取值
    fundCode = "005669"
    v = time.strftime(r'%Y%m%d%H%M%S')
    url = f"http://fund.eastmoney.com/pingzhongdata/{fundCode}.js?v={v}"
    fundData = requests.get(url).text
    
    # 现任基金经理的基本信息
    Data_currentFundManager = json.loads(re.findall(
        r"var Data_currentFundManager =([^;]*)", fundData, 0)[0])

    print(Data_currentFundManager)
