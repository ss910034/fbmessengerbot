from flask import Flask, request
from fbmq import Attachment, Template, QuickReply, Page
from ts import query_AllProduct
from Userprofile import *
from insertDB import *
from templates import *
import random
import json
import requests
from FBToken import *

########################################################
## 設置事件終點、通關密碼和認證密碼
app = Flask(__name__)
page = Page(ACCESS_TOKEN)
allProduct = query_AllProduct()
profile = {}

## 設置webhook
@app.route("/", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        else:
            return 'Invalid verification token'
    else:
        page.handle_webhook(request.get_data(as_text=True))
        return 'ok'

########################################################
## 判讀payload內容
@page.handle_postback
def received_postback(event):
    global profile
    sender_id = event.sender_id
    payload = event.postback_payload
    user_profile = page.get_user_profile(event.sender_id) # return dict

    ## 讓機器人在使用者傳送訊息後立刻已讀訊息並開啟輸入指示器(點點點符號)
    page.mark_seen(sender_id)
    page.typing_on(sender_id)

    ## 當使用者第一次打開機器人按下'開始使用'時
    if payload == 'START':
        text = 'Hi '+ user_profile['first_name'] + ' 歡迎來到 龜 婦 の 生 活 😊\n您今天來到這裡有什麼能替您服務的嗎？'
        profile[sender_id] = User(sender_id, user_profile)
        page.send(sender_id, Template.Generic([
            Template.GenericElement("歡迎來到 龜 婦 の 生 活 😊\n您今天來到這裡有什麼能替您服務的嗎？",
                          buttons=[
                              Template.ButtonPostBack('商品詢問', "query1"),
                              Template.ButtonPostBack('訂購商品', "order1"),
                              Template.ButtonPostBack('查看購物車', "Cart")
                          ])]))
    ## 當使用者按下選單中的'重新查詢'時
    elif payload == 'REFRESH':
        text = 'Hi '+ user_profile['first_name'] + ' 歡迎來到 龜 婦 の 生 活 😊\n您今天來到這裡有什麼能替您服務的嗎？'
        page.send(sender_id, text, quick_replies=[{'title': '商品詢問', 'payload': 'Y'},{'title': '訂購商品', 'payload': 'Y'}])
    

########################################################
## 設置起始按鈕與常駐選單
page.greeting('☆分享金龜婿と龜婦的台日生活\n★愛購物更ღ日貨的龜婦因此走上代購這條不歸路...\n★日本代購/網站代購(衣服.包包.帽子等)皆可私')
page.show_starting_button('START')
page.show_persistent_menu([Template.ButtonPostBack('重新查詢', 'REFRESH')])

########################################################
## 訊息傳送與判斷

@page.callback(['dealCart'], types=['POSTBACK'])
def callback_picked_genre(payload, event):
    global profile
    sender_id = event.sender_id
    count = 1
    cartSum = 0
    text = ''
    if len(profile[sender_id].orderDetail):
        for i in profile[sender_id].orderDetail:
            item = i.split(',')
            text += str(count)+".\n商品名稱："+item[1]+"\n顏色尺寸："+item[2]+"\n數量："+item[3]+"\n金額小計："+str(int(item[3])*int(item[4]))
            text += '\n-------------\n'
            count = count + 1
            cartSum += int(item[3])*int(item[4])
        text += '運費：＄60\n總金額：'+str(60+cartSum)
    page.send(sender_id, text)
    page.send(sender_id, Template.Generic([
            Template.GenericElement('商品清單',
                          buttons=[Template.ButtonPostBack('商品詢問', "query1"),
                              Template.ButtonPostBack('送出訂單', "deal")])]))

@page.callback(['deal'], types=['POSTBACK'])
def callback_picked_genre(payload, event):
    global profile
    sender_id = event.sender_id
    user_profile = page.get_user_profile(event.sender_id)
    finalOrder = ''
    my_data={}
    for item in profile[sender_id].orderDetail:
        finalOrder+=item+';'

    amount = '80,'+str(int(profile[sender_id].product_price)*int(profile[sender_id].product_Num))
    my_data['token'] = 'd31f382586b504e74655b982e6be4ed10a3a25c9'
    my_data['action'] = 'new_bf'
    my_data['fb_name'] = (user_profile['last_name']+user_profile['first_name'])
    my_data['pay_method'] = 'bank'
    my_data['amount'] = amount
    my_data['prepay'] = 0
    my_data['items'] = finalOrder
    print(my_data)
    r = requests.post('https://dev.kamefushop.tw/kf-admin/post', data = my_data)
    print(r.status_code)
    print(r.text)
    updateToDB((user_profile['last_name']+user_profile['first_name']), finalOrder)
    page.send(sender_id, 'url\n訂單已成立\n付款資訊請您點入網址\n提醒您，請在3天內匯款後填單唷\n逾期未匯款視同棄標，時間上來不及請您一定要提前通知\n商品如遇缺貨會在這邊跟您說\n有提供店到店純取貨，如需超商取件請再填單時選擇\n再麻煩您確認～謝謝😊')
    page.send(sender_id, '還有什麼能為您服務的嗎？', quick_replies=[{'title': '商品詢問', 'payload': 'Y'},
                                                {'title': '訂購商品', 'payload': 'Y'}])
    profile[sender_id].resetdata()
    profile[sender_id].resetOrdetail()

@page.callback(['Cart'], types=['POSTBACK'])
def callback_picked_genre(payload, event):
    global profile
    sender_id = event.sender_id
    user_profile = page.get_user_profile(event.sender_id)
    count = 1
    cartSum = 0
    text = ''
    if len(profile[sender_id].orderDetail):
        for i in profile[sender_id].orderDetail:
            item = i.split(',')
            text += str(count)+".\n商品名稱："+item[1]+"\n顏色尺寸："+item[2]+"\n數量："+item[3]+"\n金額小計："+str(int(item[3])*int(item[4]))
            text += '\n-------------\n'
            count = count + 1
            cartSum += int(item[3])*int(item[4])
        text += '運費：＄60\n總金額：'+str(60+cartSum)
        page.send(sender_id, text)
        page.send(sender_id, Template.Generic([
                Template.GenericElement('是否購買',
                            buttons=[Template.ButtonPostBack('送出訂單', "deal"),
                                    Template.ButtonPostBack('繼續購物', "continueBuy")])]))  
    else:
        text = '購物車還是空的呢～\n快去購物吧！！'
        page.send(sender_id, Template.Generic([
            Template.GenericElement(text,
                          buttons=[
                              Template.ButtonPostBack('商品詢問', "query1"),
                              Template.ButtonPostBack('訂購商品', "order1"),
                              Template.ButtonPostBack('查看購物車', "Cart")
                          ])]))
    
    


@page.callback(['product(.+)'])
def callback_clicked_button(payload, event):
    sender_id = event.sender_id
    message = payload.replace('product','')
    if profile[sender_id].query_price == True or profile[sender_id].buy == True:
        if message in allProduct.keys():
            profile[sender_id].product_price = allProduct[message][3]
            page.send(sender_id, "商品敘述："+allProduct[message][7])
            page.send(sender_id, Template.Generic([
                Template.GenericElement(message,
                          subtitle="商品價格："+profile[sender_id].product_price,
                          buttons=[
                              Template.ButtonPostBack("我要訂購", "wantToBuy"),
                              Template.ButtonPostBack("我考慮一下", "ddd")
                          ])]))
            # page.send(sender_id, "這個商品的價格為："+allProduct[message][3])
            # text = '是否購買此商品～'
            profile[sender_id].product_Name = message
            # page.send(sender_id, text, quick_replies=[{'title': '我要訂購', 'payload': 'Buy'},
            #                                         {'title': '我考慮一下', 'payload': 'confused'}])

@page.callback(['wantToBuy'])
def callback_clicked_button(payload, event):
    sender_id = event.sender_id
    productType = allProduct[profile[sender_id].product_Name][2].split(',')
    data = []
    for i in productType:
        data_json = json.loads('{"title": "'+ i +'", "payload": "'+ i +'"}')
        data.append(data_json)
    profile[sender_id].isChooseType = True
    if profile[sender_id].buy:
        profile[sender_id].set_buy(False)
    page.send(sender_id, "商品的款式您要選擇？", quick_replies=data)

@page.callback(['continueBuy'])
def callback_clicked_button(payload, event):
    sender_id = event.sender_id
    profile[sender_id].resetdata()
    profile[sender_id].set_queryprice(True)
    text = '請輸入您想詢問的商品名稱為何？'
    page.send(sender_id, text)

@page.callback(['order1'])
def callback_clicked_button(payload, event):
    sender_id = event.sender_id
    message = event.message_text
    text = '請輸入您想購買的商品名稱為何？'
    page.send(sender_id, text)
    profile[sender_id].set_buy(True)


@page.callback(['query1'])
def callback_clicked_button(payload, event):
    sender_id = event.sender_id
    message = event.message_text
    profile[sender_id].set_queryprice(True)
    text = '請輸入您想詢問的商品名稱為何？'
    page.send(sender_id, text)

@page.handle_message
def message_handler(event):
    global profile
    global allProduct
    sender_id = event.sender_id
    message = event.message_text
    

    ## 如果程式重啟，判斷有沒有使用者資料，若無，則initial使用者資訊
    if not profile:
        user_profile = page.get_user_profile(event.sender_id) # return dict
        profile[sender_id] = User(sender_id, user_profile)

    ## 讓機器人在使用者傳送訊息後立刻已讀訊息並開啟輸入指示器(點點點符號)
    page.mark_seen(sender_id)
    page.typing_on(sender_id)
    ## 當使用者一開始回答'商品詢問'的回應

    if message == '商品詢問':
        profile[sender_id].set_queryprice(True)
        text = '請輸入您要詢問的商品名稱？'
        page.send(sender_id, text)

    elif message == '訂購商品':
        text = '請輸入您想購買的商品名稱為何？'
        page.send(sender_id, text)
        profile[sender_id].set_buy(True)

    elif profile[sender_id].buy == True and message != '我要訂購':
        if message in allProduct.keys():
            profile[sender_id].product_price = allProduct[message][3]
            page.send(sender_id, Template.Generic([
                Template.GenericElement(message,
                          subtitle="商品價格："+profile[sender_id].product_price+"\n商品敘述："+allProduct[message][7],
                          buttons=[
                              Template.ButtonPostBack("我要訂購", "12"),
                              Template.ButtonPostBack("我考慮一下", "ddd")
                          ])]))
            page.send(sender_id, "這個商品的價格為："+allProduct[message][3])
            text = '是否購買此商品～'
            profile[sender_id].product_Name = message
            page.send(sender_id, text, quick_replies=[{'title': '我要訂購', 'payload': 'Buy'},
                                                    {'title': '我考慮一下', 'payload': 'confused'}])
        else:
            has = False
            data = []
            data_Generic = []
            for key in allProduct.keys():
                if key.find(message) != -1:
                    has = True
                    data.append(key)
            if has == True:
                for i in data:
                    tmp = Template.GenericElement(str(i),
                          subtitle="",
                          item_url=str(allProduct[i][6]),
                          image_url=str(allProduct[i][5]),
                          buttons=[Template.ButtonPostBack(str(i), 'product'+str(i))])
                    data_Generic.append(tmp)
                page.send(sender_id, Template.Generic(data_Generic))
            else:
                page.send(sender_id, '您確定要查詢的商品名稱正確嗎～\n我還有什麼能為您服務的嗎？', quick_replies=[{'title': '商品詢問', 'payload': 'Y'},
                                                {'title': '訂購商品', 'payload': 'Y'}])
                profile[sender_id].buy = False

    elif (profile[sender_id].query_price == True or profile[sender_id].buy ==True) and message == '我要訂購':
        productType = allProduct[profile[sender_id].product_Name][2].split(',')
        data = []
        for i in productType:
            data_json = json.loads('{"title": "'+ i +'", "payload": "'+ i +'"}')
            data.append(data_json)
        profile[sender_id].isChooseType = True
        if profile[sender_id].buy:
            profile[sender_id].set_buy(False)
        page.send(sender_id, "商品的款式您要選擇？", quick_replies=data)

    elif profile[sender_id].isChooseType == True:
        profile[sender_id].product_Type = message
        productSize = allProduct[profile[sender_id].product_Name][4].split(';')
        data = []
        for i in productSize:
            data_json = json.loads('{"title": "'+ i +'", "payload": "'+ i +'"}')
            data.append(data_json)
        profile[sender_id].isChooseType = False
        profile[sender_id].isChooseSize = True
        page.send(sender_id, "商品的尺寸為？", quick_replies=data)

    elif profile[sender_id].isChooseSize == True:
        profile[sender_id].product_Size = message
        profile[sender_id].isChooseSize = False
        profile[sender_id].isChooseNum = True
        page.send(sender_id, "請輸入您要購買的數量：", quick_replies=[{'title': '1', 'payload': 'one'},
                                                  {'title': '2', 'payload': 'two'},
                                                  {'title': '3', 'payload': 'three'},
                                                  {'title': '4', 'payload': 'four'},
                                                  {'title': '5', 'payload': 'five'}])

    elif profile[sender_id].isChooseNum == True:
        profile[sender_id].product_Num = message
        profile[sender_id].isChooseNum = False
        orderList = allProduct[profile[sender_id].product_Name][1]+','+profile[sender_id].product_Name+','+profile[sender_id].product_Size+'/'+profile[sender_id].product_Type+','+profile[sender_id].product_Num+','+profile[sender_id].product_price
        profile[sender_id].orderDetail.append(orderList)
        text = "已將商品/顏色/尺寸/數量："+profile[sender_id].product_Name+"/"+profile[sender_id].product_Type+"/"+profile[sender_id].product_Size+"/"+profile[sender_id].product_Num+"\n加到購物車囉,接下來呢？"
        page.send(sender_id, text)
        page.send(sender_id, Receipttemplate(recipient_name=profile[sender_id].product_Name, order_number='temp', currency='TWD', payment_method='銀行匯款',
                 timestamp="20200311", elements=None, address=None, summary={
          "total_cost":profile[sender_id].product_price
        }, adjustments=None))
        # print(orderList)
        page.send(sender_id, Template.Generic([
            Template.GenericElement("還想要再購買其他的商品嗎～",
                          buttons=[
                              Template.ButtonPostBack('繼續購物', "continueBuy"),
                              Template.ButtonPostBack('送出訂單', "dealCart"),
                              Template.ButtonPostBack('查看購物車', "Cart")
                          ])]))

    elif message == '我考慮一下' or message == '重新訂購～':
        # profile[sender_id].resetdata()
        page.send(sender_id, '有什麼能為您服務的嗎？', quick_replies=[{'title': '商品詢問', 'payload': 'Y'},
                                                {'title': '訂購商品', 'payload': 'Y'}])
    elif profile[sender_id].query_price == True:
        if message in allProduct.keys():
            profile[sender_id].product_price = allProduct[message][3]
            page.send(sender_id, message+"\n"+allProduct[message][7]+"這個商品的價格為："+allProduct[message][3])
            text = '是否購買此商品～'
            profile[sender_id].product_Name = message
            page.send(sender_id, text, quick_replies=[{'title': '我要訂購', 'payload': 'Buy'},
                                                    {'title': '我考慮一下', 'payload': 'confused'}])
        else:
            has = False
            data = []
            data_Generic = []
            for key in allProduct.keys():
                if key.find(message) != -1:
                    has = True
                    data.append(key)
            if has == True:
                for i in data:
                    tmp = Template.GenericElement(str(i),
                          subtitle="",
                          item_url=str(allProduct[i][6]),
                          image_url=str(allProduct[i][5]),
                          buttons=[Template.ButtonPostBack(str(i), 'product'+str(i))])
                    data_Generic.append(tmp)
                page.send(sender_id, Template.Generic(data_Generic))
            else:
                page.send(sender_id, '您確定要查詢的商品名稱正確嗎～\n我還有什麼能為您服務的嗎？', quick_replies=[{'title': '商品詢問', 'payload': 'Y'},
                                                {'title': '訂購商品', 'payload': 'Y'}])
                profile[sender_id].query_price = False
    elif message != '送出訂單':
        page.send(sender_id, '您確定要查詢的商品名稱正確嗎～\n我還有什麼能為您服務的嗎？', quick_replies=[{'title': '商品詢問', 'payload': 'Y'},
                                                {'title': '訂購商品', 'payload': 'Y'}])


########################################################
## 執行程式
if __name__ == '__main__':
    app.run()