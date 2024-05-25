import re
from typing import List, Union

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet as bs4ResultSet
from fake_useragent import UserAgent
from tqdm import tqdm
from typing_extensions import Annotated

ua = UserAgent()


def extractRelationCompanyCodeFromScriptTag(
    tag: Annotated[bs4ResultSet, "company script tag"]
) -> [Annotated[str, "company code"], Annotated[str, "company name"]]:
    """
    從 HTML 的 Script 標籤中提取公司代碼和名稱

    Parameters:
        tag : bs4ResultSet
            公司資訊的 Script 標籤

    Returns:
        [str, str]
            公司代碼和公司名稱

    Example:
        tag.text: "\r\n<!--\r\n\tGenLink2stk('AS1104','環泥');\r\n//-->\r\n"
        return: ['1104', '環泥']
    """
    result = re.sub("\r\n|\t|<!--|;|-->|//|'|AS", "", tag.text)  # 去除不需要的字符
    result = re.findall(
        pattern="GenLink2stk\((.*)\)", string=result
    )  # 提取 GenLink2stk 中的內容
    result = result[0]  # 取出列表中的第一個元素
    code, name = result.split(",")  # 分割代碼和名稱
    return code, name  # 返回公司代碼和名稱


def getStockRelationData(stock_code: Annotated[Union[str, int], "stock code"]):
    """
    獲取特定股票代碼的公司關係

    Parameters:
        stock_code : Union[str, int]
            股票代碼

    Returns:
        pd.DataFrame
            公司關係的 DataFrame

    Example:
        stock_code: 2330
        return:
                main_code    relation  code   name
            0         2330      供應商  1104   環泥
            1         2330      供應商  1560   中砂
            2         2330      供應商  1595   川寶
            3         2330      供應商  1597   直得
            4         2330      供應商  1711   永光
            ..         ...      ...   ...  ...
            137       2330       客戶  8299   群聯
            138       2330      轉投資  3374   精材
            139       2330      轉投資  3443   創意
            140       2330      轉投資  5347   世界
            141       2330      轉投資  6789   采鈺
    """
    user_agent = ua.random

    # 設置 HTTP requests header
    hdr = {"user-agent": user_agent}

    # 發送 HTTP requests
    url = f"https://fubon-ebrokerdj.fbs.com.tw/Z/ZC/ZC0/ZC00/ZC00_{stock_code}.djhtm"
    page = requests.get(url, headers=hdr)

    # 解析 HTML
    soup = BeautifulSoup(page.content, "html.parser", from_encoding="cp950")

    # 取得所有關係的類別
    relationship_category = soup.findAll("td", {"class": "t2"})
    relationship_category = [
        category.text for category in relationship_category
    ]  # ['供應商', '競爭者', '客戶', '轉投資', '被投資', '策略聯盟']

    # 取得所有關聯公司
    relationship_companys = soup.findAll("td", {"class": "t3t1"})
    companys_list = [
        res_comp.findAll("script") for res_comp in relationship_companys
    ]  # 提取 Script 標籤中的公司信息, 每個 element 紀錄某種關係下的公司

    df_list = []
    for relationship, companys in zip(relationship_category, companys_list):
        temp_df = pd.DataFrame(
            [extractRelationCompanyCodeFromScriptTag(company) for company in companys],
            columns=["code", "name"],
        )
        temp_df.insert(loc=0, column="relation", value=relationship)
        temp_df.columns  # Index(['relation', 'code', 'name'], dtype='object')
        df_list.append(temp_df)

    df = pd.concat(df_list).reset_index(drop=True)
    df.insert(loc=0, column="main_code", value=stock_code)
    return df


def getStockRankOfMarketValueData() -> Annotated[
    pd.core.frame.DataFrame, "company rank of market value(suset)"
]:
    """
    獲取公司市場價值排名數據

    Returns:
        pd.DataFrame
            公司市值的 DataFrame

    Example:
        return:
                rank   code   name
            0       0  2330  台積電
            1       1  2317   鴻海
            2       2  2454  聯發科
            3       3  2382   廣達
            4       4  2412  中華電
            ..    ...   ...  ...
            489   489  6438   迅得
            490   490  6277   宏正
            491   491  1201   味全
            492   492  1535   中宇
            493   493  2464   盟立
    """
    user_agent = ua.random
    hdr = {"user-agent": user_agent}  # 設置 HTTP requests header
    page = requests.get(
        "https://www.taifex.com.tw/cht/9/futuresQADetail", headers=hdr
    )  # 發送 HTTP requests
    soup = BeautifulSoup(page.content, "html.parser")
    rank_list = soup.findAll("td", {"align": "right", "headers": "name_a"})
    rank_list = [
        re.sub(pattern="\r|\n|\t| ", repl="", string=tag.text) for tag in rank_list
    ]  # 去除不需要的字符
    rank_df = pd.DataFrame(
        [[rank_list[i], rank_list[i + 1]] for i in range(0, len(rank_list), 2)],
        columns=["code", "name"],
    )
    rank_df = rank_df.reset_index().rename(columns={"index": "rank"})
    return rank_df


def getListedStockCodeData() -> Annotated[
    List[str], "list object of stock code which are listed"
]:
    """
    獲取所有上市公司的股票代碼

    Returns:
        List[str]
            所有上市公司股票代碼的列表

    Example:
        return:
            ['1101', '1102', '1103', ..., '9945', '9946', '9955', '9958']
    """
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
    resp = requests.get(url=url)
    return [sub_dict["公司代號"] for sub_dict in resp.json()]


# Example
# 取得公司市值排序
rank_df = getStockRankOfMarketValueData()
# 篩選市值前 100 大的公司
rank_df = rank_df.query("rank < 5")
df_list = []
for rank, code, name in tqdm(rank_df.values):
    df = getStockRelationData(stock_code=code)
    df_list.append(df)

# 第一家公司的關係列表
df_list[0]
