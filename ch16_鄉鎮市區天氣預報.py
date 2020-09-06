# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 22:23:11 2020

@author: Johnson Lo
"""
import pandas as pd
import requests
import os
from bs4 import BeautifulSoup


#檢查是否已存在鄉鎮市區代碼檔
if not os.path.isfile("district.csv"):
    url = "https://www.stat.gov.tw/public/Attachment/712693030RPKUP4RX.xlsx"
    df = pd.read_excel(url, header=3)
    df.drop(columns=["縣市代碼", "村里代碼", "村里名稱", "村里代碼.1"], axis=1, inplace=True)
    df.drop_duplicates(inplace=True)
    df.to_csv("district.csv", encoding="big5", index=False)
    
dftown = pd.read_csv("district.csv", encoding="big5")
town = input("請輸入查詢的鄉鎮市區名稱: ")
dfs = dftown[(dftown["縣市名稱"]==town[:3]) & (dftown["區鄉鎮名稱"]==town[3:])]

if len(dfs) > 0:   # 區鄉鎮名稱若存在
    town_no = str(dfs.iloc[0, 1])   # ????????????????????????????????? 這是本段code唯一不清楚的取值範圍
    url = "https://www.cwb.gov.tw/V8/C/W/Town/MOD/3hr/" + town_no + "_3hr_PC.html"
    resp = requests.get(url)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml") 

    # 整理日期時間欄
    for t in soup.find_all("span", class_="t"):
        t.replaceWith(t.text + ",")
    for d in soup.find_all("span", class_="d"):
        d.replaceWith(d.text)    
    # 整理天氣示意圖欄位
    for img in soup.find_all("img"):
        img.replaceWith(img.get("alt"))  
    # 整理溫度及體感溫度欄
    for c in soup.find_all("span", class_="tem-C"):
        c.replaceWith(c.text)
    for f in soup.find_all("span", class_="tem-F"):
        f.replaceWith("")    
    # 整理蒲級風速
    for w1 in soup.find_all("span", class_="wind_1"):
        w1.replaceWith(w1.text + ",")
    for w2 in soup.find_all("span", class_="wind_2"):
        w2.replaceWith("")

    # 最後才用pandas讀取表格來處理
    df = pd.read_html(str(soup))[0]   # soup是個soup物件, 所以必須把它字串化, 加str, 才能讓real_html讀進去
    df1 = df.T
    # 刪除不必要的欄位
    df1.drop(columns=[1, 3, 5, 7, 9, 11], axis=1, inplace=True)
    # 重設索引
    df1.reset_index(inplace=True)
    # 將index拆分成 "時間,日期" 二個欄位
    df1[["時間", "日期"]] = df1["index"].str.split(",", expand=True)
    # 將第10欄位也拆分成 "蒲福風級, 風向" 二個欄位
    df1[["蒲福風級", "風向"]] = df1[10].str.split(",", expand=True)
    # 刪除index及10 二個欄位
    df1.drop(columns=["index", 10], inplace=True)
    # 修改欄位名稱
    columns = ["天氣狀況", "溫度", "降雨機率", "體感溫度", "相對濕度", "舒適度", "時間","日期", "蒲福風級", "風向"]
    df1.columns = columns
    # 欄位重新排列
    df1 = df1[[ "時間","日期", "天氣狀況", "溫度", "降雨機率", "體感溫度", "相對濕度", "舒適度", "蒲福風級", "風向"]]
    # 轉為json回傳
    print(df1.to_json(orient="records", force_ascii=False))
else:
    print("無此鄉鎮市場名稱")