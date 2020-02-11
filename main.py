import os
import apiai
import json
import requests
import random
from geopy.distance import geodesic
from graphqlclient import GraphQLClient

from algoliasearch.search_client import SearchClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageSendMessage,
    LocationMessage,
    CarouselTemplate, CarouselColumn, URIAction,
    TemplateSendMessage, ButtonsTemplate, URITemplateAction,
)

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
SECRET = os.environ.get('SECRET')
DIALOGFLOW_CLIENT_ACCESS_TOKEN = os.environ.get('DIALOGFLOW_CLIENT_ACCESS_TOKEN')

ALGOLIA_APP_ID = os.environ.get('ALGOLIA_APP_ID')
ALGOLIA_APP_KEY = os.environ.get('ALGOLIA_APP_KEY')
ALGOLIA_APP_INDEX = os.environ.get('ALGOLIA_APP_INDEX')

GRAPHQL_URL = os.environ.get('GRAPHQL_URL')

ql_client = GraphQLClient(GRAPHQL_URL)

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_APP_KEY)
index = client.init_index(ALGOLIA_APP_INDEX)

ai = apiai.ApiAI(DIALOGFLOW_CLIENT_ACCESS_TOKEN)
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

# 3. 使用 qraphql client 抓取即時口罩資料
result = ql_client.execute('''
    query {
      getMasks  {
        payload{
          ## 醫事機構代碼
          code
          ## 成人口罩總剩餘數
          adult_count
          ## 兒童口罩剩餘數
          child_count
          ## 來源資料時間
          updated_at
        }
        message
        errors
        status
      }
    }
    ''')
ql_result = json.loads(result)['data']['getMasks']['payload']

def callback(request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ================= 機器人區塊 Start =================
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    msg = event.message.text # message from user
    uid = event.source.user_id # user id
    # 1. 傳送使用者輸入到 dialogflow 上
    ai_request = ai.text_request()
    #ai_request.lang = "en"
    ai_request.lang = "zh-tw"
    ai_request.session_id = uid
    ai_request.query = msg

    # 2. 獲得使用者的意圖
    ai_response = json.loads(ai_request.getresponse().read())
    user_intent = ai_response['result']['metadata']['intentName']

    # 3. 根據使用者的意圖做相對應的回答
    if user_intent == "CanGetMask":
        # 建立一個 button 的 template
        buttons_template_message = TemplateSendMessage(
            alt_text="告訴我你現在的位置",
            template=ButtonsTemplate(
                text="告訴我你現在的位置",
                actions=[
                    URITemplateAction(
                        label="Send my location",
                        uri="line://nv/location"
                    )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            buttons_template_message)

    else: # 聽不懂時的回答
        msg = "Sorry，I don't understand"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 1. 獲取使用者的經緯度
    lat = event.message.latitude
    lng = event.message.longitude
    # print(str(event))

    # 2. 使用 Algolia 做 geo search 取得離目前最近的 6 個特約店家 =========
    origin = (lat, lng)
    hits = index.search('', {
        'aroundLatLng': origin,
        'aroundRadius': 3000, # 3km
        'hitsPerPage': 6
    })
    if (int(len(hits['hits']) < 1)):
        msg = "抱歉，查無資料"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
        exit()

    columnObjs=[]
    for location in hits['hits']:
        # 4. 使用 geodesic 計算兩點距離
        destination = (location['_geoloc']["lat"], location['_geoloc']["lng"])
        location_distance = int(geodesic(origin, destination).meters)
        
        # 5. 取得依照 code (特約機關代碼) 取得口罩數量及最後更新時間
        mask = list(filter(lambda x:x["code"]==location["objectID"], ql_result))
        adult_count = "0" if len(mask) < 1 else mask[0]['adult_count']
        child_count = "0" if len(mask) < 1 else mask[0]['child_count']
        updated_at = "無" if len(mask) < 1 else mask[0]['updated_at']

        distance = "沒有資料" if location_distance is None else location_distance
        address = "沒有資料" if location.get("address") is None else location["address"]
        phone = "沒有資料" if location.get("phone") is None else location["phone"]
        details = "成人口罩：{}\n孩童口罩：{}\n最後更新時間： {}".format(adult_count, child_count, updated_at)

        # 6. 取得 Google map 網址
        map_url = "https://www.google.com/maps/search/?api=1&query={lat},{lng}".format(
            lat=location['_geoloc']["lat"],
            lng=location['_geoloc']["lng"],
        )

        # 建立 CarouselColumn obj
        column = CarouselColumn(
            thumbnail_image_url='https://storage.googleapis.com/mask-taiwan-2020/mask.png',
            title="{}(約 {} 公尺)".format(location['name'], distance),
            text=details,
            actions=[
                URIAction(
                    label=address,
                    uri=map_url
                ),
                URIAction(
                    label=phone, 
                    uri=str('tel:' + phone)
                )
            ]
        )
        # 加入 list
        columnObjs.append(column)

    # 回覆使用 Carousel Template
    carousel_template_message = TemplateSendMessage(
        alt_text='選出最近的六個口罩購買地點及資訊給你',
        template=CarouselTemplate(
            columns=columnObjs
        )
    )

    try:
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message)
    except:
        print(str(columnObjs))
