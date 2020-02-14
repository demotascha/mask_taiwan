# Mask Taiwan

![image](https://storage.googleapis.com/mask-taiwan-2020/MaskTaiwan-Line.jpg)

## Proposal
藉由 『我罩你』 LineBot，簡單找到醫療特約藥局口罩資訊。

## Concept
- 開發資源於[口罩供需資訊平台](https://g0v.hackmd.io/gGrOI4_aTsmpoMfLP1OU4A?view#%E5%85%B6%E4%BB%96%E6%87%89%E7%94%A8)
    - 透過 [藥局+衛生所即時庫存 geojson by kiang](https://raw.githubusercontent.com/kiang/pharmacies/master/json/points.json) 取得特約藥局相關資訊(json)
    - 透過 [即時庫存 Proxy GraphQL 版, from Front-End Developers Taiwan by 懷恩](https://mask-data-farmer.herokuapp.com/graphql)取得即時藥局口罩資訊
- dialogflow 取得使用者意圖（CanGetMask）
- 使用 Line 內建方式取得使用者的位置
- 依照使用者所提供的位置至 Algolia 的 `geoserach` 功能，處理 nearby (經緯度、距離<3km、回傳6筆)
- 使用 geopy.distance 計算使用者與藥局距離（公尺）

## 準備項目
- Line@ developer
- 建立一個 GCP 專案
- 透過 tools 建立醫療特約藥局基本資訊至 algolia
- 在 GCP 上授權 Dialogflow 專案
- 建立 Cloud Function

### Dialogflow.com

定義 intents, entities, fulfillment

### cloud function

- 設定來源
- 環境變數

```
ACCESS_TOKEN (from LINE)
SECRET (from LINE)
GOOGLE_API_KEY (from Google, 記得要同時啟用 Google Map Distance Matrix API)
DIALOGFLOW_CLIENT_ACCESS_TOKEN (from dialogflow)
ALGOLIA_APP_ID (from Algolia)
ALGOLIA_APP_KEY (from Algolia)
ALGOLIA_APP_INDEX (from Algolia)
GRAPHQL_URL（from `https://mask-data-farmer.herokuapp.com/graphql`）
DATA_RESOURCE_URL (from `https://raw.githubusercontent.com/kiang/pharmacies/master/json/points.json`)
```

## 推廣時間

- Youtube 簡易功能介紹：https://youtu.be/E0b1zDn1V_I
- Linebot (https://lin.ee/tv207Kf)

![image](https://storage.googleapis.com/mask-taiwan-2020/S.png)


### references:
- 開發資源 [口罩供需資訊平台](https://g0v.hackmd.io/gGrOI4_aTsmpoMfLP1OU4A?view#%E5%85%B6%E4%BB%96%E6%87%89%E7%94%A8)
- [藥局+衛生所即時庫存 geojson by kiang](https://raw.githubusercontent.com/kiang/pharmacies/master/json/points.json) 取得特約商店相關資訊(json)
- [即時庫存 Proxy GraphQL 版, from Front-End Developers Taiwan by 懷恩](https://mask-data-farmer.herokuapp.com/graphql)取得即時口罩資訊
- [用Dialogflow建立LINE Chatbot](https://medium.com/@wolkesau/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8dialogflow%E5%BB%BA%E7%AB%8Bchatbot-1-%E4%BB%8B%E7%B4%B9-62736bcdad95)
- [DIALOGFLOW](https://cloud.google.com/dialogflow/?hl=zh-TW)
