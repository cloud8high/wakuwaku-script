from bs4 import BeautifulSoup
import requests
import datetime
import json
import random
import time
import os

# SETTINGS ユーザ情報入力
payload_userinfo = {
    'utf8': '✓',
    'user[email]': os.environ['email'], # メールアドレス
    'user[password]': os.environ['password'], # パスワード
    'user[remember_me]': '0'
}

# CONSTANT 日時情報
dt_today = datetime.date.today() # >>> 2020-06-20


# PROCESSING
def lambda_handler(event, context):
    # ログイン画面にて、authenticity_tokenの取得
    s = requests.Session()
    res_login1 = s.get('https://pepup.life/users/sign_in')
    soup_login1 = BeautifulSoup(res_login1.text, 'html.parser')
    auth_token = soup_login1.find(attrs={'name': 'authenticity_token'}).get('value')
    # print(auth_token)

    # ログイン実行
    payload_userinfo['authenticity_token'] = auth_token # tokenをpayloadに追加
    res_login2 = s.post('https://pepup.life/users/sign_in', data=payload_userinfo)

    # 一括入力画面のURL生成
    dt_now = datetime.datetime.now()
    print(dt_now)
    year = str(dt_now.year)
    month = str(dt_now.month)
    day = str(dt_now.day)
    batchpath = 'https://pepup.life/scsk_mileage_campaigns/' + year + '/' + month + '/' + day
    # print(path) # >>> https://pepup.life/scsk_mileage_campaigns/2020/6/20

    # 一括入力画面に遷移し、チェックボックスの入力に必要なcsrfTokenの取得
    res_batchday = s.get(batchpath)
    soup_batchday = BeautifulSoup(res_batchday.text, 'html.parser')
    data_batchday = soup_batchday.find(attrs={'class': 'react-data'}).get('data') # Tokenが記載された<data>タグ内情報を取得
    batchday_temp = json.loads(data_batchday)
    batchday_token = batchday_temp['csrfToken'] # Tokenを取り出し
    # print(batchday_token)
    
    # チェックボックスの入力関数
    def fill_in_checkbox(act_thing_id):
        payload_checkbox = {
            'authenticity_token': batchday_token,
            'act_fact[act_thing_id]': act_thing_id,
            'act_fact[date]': dt_today
        }
        res_checkbox = s.post('https://pepup.life/act_fact', data=payload_checkbox)
        # print('\n act_thing_id : ' + str(act_thing_id))
        # print(res_checkbox.text)

    # チェックボックスの入力処理を送信 (csrfTokenを内部で利用)
    fill_in_checkbox(48)  # 睡眠　 - 48 - 「自分にとって良い睡眠習慣を実行する」
    fill_in_checkbox(49)  # アルコール - 49 - 「アルコール摂取20g以内（休肝日含む）」
    fill_in_checkbox(50)  # 食生活 - 50 - 「糖分を多く含む清涼飲料水を飲まない」
    fill_in_checkbox(51)  # 食生活 - 51 - 「糖質を多く含む間食を控える」
    fill_in_checkbox(52)  # 食生活 - 52 - 「夕食（飲酒）後の夜食（締め）を食べない」
    fill_in_checkbox(1)   # 食生活 -  1 - 「朝食を食べる」
    fill_in_checkbox(6)   # 食生活 -  6 - 「ごはんを普通盛にする・おかわりしない」
    fill_in_checkbox(223) # 口腔ケア - 223 -「口腔ケア」

    # 歩数と睡眠時間入力のためのデータ準備
    timestamp = str(dt_today) + 'T00:00:00.000Z' # >>> 2020-06-20T00:00:00.000Z
    steps = str(random.randint(7200,8200)) # 歩数を7200以上8200未満のランダムな整数から選択
    sleeping_hours = str(random.randrange(360,481,30)) #睡眠時間を6時間から7時間半の間でランダムに選択
    payload_steps_text = {
        "source":"web",
        "source_uid":"web",
        "step_count":[
            {
                "value":steps,
                "timestamp":timestamp
                }
        ],
        "sleeping":[
            {
                "value":sleeping_hours,
                "timestamp":timestamp
            }
        ]
    }

    # 歩数と睡眠時間を送信
    payload_steps_json = json.dumps(payload_steps_text) # JSON形式にパース
    headers = {'content-type': 'application/json'}
    res_steps = s.post('https://pepup.life/api/v2/@me/measurements', data=payload_steps_json, headers=headers)
    # print(res_steps.text)　# >>> {"result":true}

    # ログアウト処理
    payload_data = '_method=delete&authenticity_token=' + batchday_token
    res_logout = s.post('https://pepup.life/users/sign_out', data=payload_data)
    # print(res_logout.status_code) # >>>204 (200番台なら成功)
    
    return res_logout.status_code

