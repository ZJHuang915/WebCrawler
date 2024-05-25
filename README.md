這個專案包含兩個網頁數據抓取任務:

### Fubon Company Relation Crawler
1. FubonCompanyRelationCrawler.py: 抓取特定股票的公司關係數據，包括供應商、競爭者、客戶、轉投資等。

功能
- `extractRelationCompanyCodeFromScriptTag(tag)`: 從 HTML 的 Script 標籤中提取公司代碼和名稱。
- `getStockRelationData(stock_code)`: 獲取特定股票代碼的公司關係數據。
- `getStockRankOfMarketValueData()`: 獲取公司市場價值排名數據。
- `getListedStockCodeData()`: 獲取所有上市公司的股票代碼。

使用範例
```
# 取得公司市值排序
rank_df = getStockRankOfMarketValueData()
# 篩選市值前100大的公司
rank_df = rank_df.query("rank < 100")
df_list = []
for rank, code, name in tqdm(rank_df.values):
    df = getStockRelationData(stock_code=code)
    df_list.append(df)

# 第一家公司的關係列表
df_list[0]
```

### IG Followers Crawler
2. IGFollowersCrawler.py：抓取 Instagram 用戶的追蹤者清單。

功能
- `User`: 定義 User 模組，用於存儲關注者的信息。
- `scrapingInstegramFollowers(login_account, login_password, target_account, max_scroll)`: 用於抓取 Instagram 指定用戶的關注者。

使用範例
```
result_list = scrapingInstegramFollowers(
    login_account="LOGINACCOUNT",
    login_password="LOGINPASSWORD",
    target_account="arielsvlog_816",
    max_scroll=50,
)
print(result_list[0].account)  # First Follower Account
print(result_list[0].name)  # First Follower Name
print(result_list[0].url)  # First Follower Page Url

result_dict = []
for result in result_list:
    result_dict.append(
        {"account": result.account, "name": result.name, "url": result.url}
    )
```
備註: `LOGINACCOUNT` 要換成你的帳號, `LOGINPASSWORD` 要換成你的密碼
