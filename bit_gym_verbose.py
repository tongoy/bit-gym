# -*- coding: utf-8 -*-
# BY: OUYANG TONG
# E-MAIL: 524309963@qq.com



"""
BIT gym script.
"""

import os
import time
import json
import argparse
import requests
import datetime
import webbrowser

from selenium import webdriver
from http.cookiejar import Cookie
from urllib.parse import quote, unquote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


url = {}
url['login'] = 'http://gym.dazuiwl.cn/h5/#/pages/login/login'
url['login_1'] = 'http://gym.dazuiwl.cn/third/connect/campus'
url['user_info'] = 'http://gym.dazuiwl.cn/api/user/index'

# url['venues_info'] = 'http://gym.dazuiwl.cn/api/venue/index?page=1&limit=10'
url['venues_info'] = 'http://gym.dazuiwl.cn/api/venue/index'

# url['sport_events_info'] = 'http://gym.dazuiwl.cn/api/sport_events/index?venue_id=12'
url['sport_events_info'] = 'http://gym.dazuiwl.cn/api/sport_events/index'

# url['sport_event_open_times'] = 'http://gym.dazuiwl.cn/api/sport_events/open_times/id/34?page=0&limit=7&get_days=0'
url['sport_event_open_times'] = 'http://gym.dazuiwl.cn/api/sport_events/open_times/id/{:d}'

# url['sport_event_hours'] = 'http://gym.dazuiwl.cn/api/sport_events/hour/id/34'
url['sport_event_hours'] = 'http://gym.dazuiwl.cn/api/sport_events/hour/id/{:d}'

# url['sport_event_fields'] = 'http://gym.dazuiwl.cn/api/sport_events/field/id/34'
url['sport_event_fields'] = 'http://gym.dazuiwl.cn/api/sport_events/field/id/{:d}'

# url['sport_schedule_booked'] = 'http://gym.dazuiwl.cn/api/sport_schedule/booked/id/34?day=2022-05-15'
url['sport_schedule_booked'] = 'http://gym.dazuiwl.cn/api/sport_schedule/booked/id/{:d}?day={:s}'


url['submit'] = 'http://gym.dazuiwl.cn/api/order/submit'


config_file = 'bit_gym.json'
html_file = 'bit_pay.html'


# The script uses selenium+chromedriver to login the system, because the encryption of the password is unknown.
def login(u, p):
    r'''
    The first step is to login the account of the user in BIT.

    There are several variables necessary for the following steps: state, cookie, ticket, token.
    '''
    r = requests.get(url['login_1'], allow_redirects=True)
    # print(r.url)
    # print(r.status_code)
    # print(r.encoding)
    # print(r.text)
    # print(r.headers)
    # print(r.json())
    # print(r.cookies)
    # print(r.history)

    state = unquote(r.url).split('=')[-1] # 'd270c67922a4d7488c151b93e85141a3'

    # print(len(r.history)) # 2

    r_0 = r.history[0]
    phpsessid = r_0.headers['Set-Cookie'] # 'PHPSESSID=kouf8ivt97dh8bd08gvtpdnpac; path=/'
    # print(phpsessid)
    phpsessid = phpsessid.split(';')[0]
    # print(phpsessid)

    # login r.url with selenium
    # headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    chrome_options.add_experimental_option('w3c', False)
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps, options=chrome_options)

    driver.get(r.url)
    # print(driver.current_url)
    time.sleep(5)

    driver.find_element_by_id("username").send_keys(u)
    driver.find_element_by_id("password").send_keys(p)
    login_btn = driver.find_element_by_id("login_submit")
    login_btn.click()
    time.sleep(5)

    browser_log_list = driver.get_log("performance")
    # print(len(browser_log_list))
    # print(browser_log_list)

    logs = [json.loads(log['message'])['message'] for log in browser_log_list]
    with open('./log.json', 'w') as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

    # # find the ticket
    # ticket = None
    # for log in browser_log_list:
    #     message = json.loads(log['message'])['message']
    #     if 'method' in message and message['method'] == 'Network.responseReceivedExtraInfo':
    #         if 'params' in message and 'headers' in message['params'] and 'Location' in message['params']['headers']:
    #             value = message['params']['headers']['Location']
    #             print(value)
    #             value = value.split('&')[-1]
    #             if value.startswith('ticket='):
    #                 ticket = value.split('=')[-1]
    #                 break
    # print(ticket)



    # find the very important variable: token
    token= None
    for log in browser_log_list:
        message = json.loads(log['message'])['message']
        if 'method' in message and message['method'] == 'Network.requestWillBeSent':
            if 'params' in message and 'request' in message['params'] and 'url' in message['params']['request']:
                request_url = message['params']['request']['url']
                # print(request_url)
                if request_url == url['user_info']:
                    if 'headers' in message['params']['request']:
                        token = message['params']['request']['headers']['token']
                        break

    # print(token)
    driver.quit()

    
    # print(driver.get_cookies())

    # headers = {'token': token}
    

    # r = requests.get(url['user_info'], headers={'token': token}, cookies=dict(PHPSESSID=phpsessid))
    # r = requests.get(url['user_info'], headers={'token': token})
    cookie_name, cookie_value = phpsessid.split('=')
    cookie = {cookie_name: cookie_value}
    r = requests.get(url['user_info'], headers={'token': token}, cookies=cookie)
    if r.status_code == requests.codes.ok:
        # print("\n\n\nLogin Done.\n")
        # print(type(r.json())) # <class 'dict'>
        # print(r.json())

        user_info = r.json()
        if user_info['data']['verification']['mobile']:
            print("\n\n\nHi, {:s}({:s}, {:s}).".format(user_info['data']['name'], user_info['data']['nickname'], user_info['data']['mobile']))
        else:
            print("\n\n\nHi, {:s}({:s}).".format(user_info['data']['name'], user_info['data']['nickname']))
        
    else:
        # print(r.json())
        print("\n\n\nLogin failed. Please try again.")
        exit()

    
    # print(r.encoding)
    # print(r.status_code)
    # print(r.json())

    return cookie, token, user_info


def wants(cookies, token, day=1, sport=1):
    # print(cookies, token)


    ### get venues info
    r = requests.get(url['venues_info'], cookies=cookies)
    venues_info = r.json()
    # print(venues_info)
    venue_info = venues_info['data']['list'][0]
    venue_id = venue_info['id']
    venue_name = venue_info['name']

    print("\nGym: {:s}(id={:d})".format(venue_name, venue_id))
    print("Appointment: {:s} - {:s}".format(venues_info['data']['appointment_begin_time'], venues_info['data']['appointment_end_time']))

    
    ### get sport events info: [table tennis(id=33), badminton(id=34), tennis(id=35)].
    r = requests.get(url['sport_events_info'], params={'venue_id': venue_id}, cookies=cookies)
    # print(r.url)
    sport_events_info = r.json()
    # print(sport_events_info)
    sport_event_info = sport_events_info['data']['list'][sport] # [table tennis, badminton, tennis]
    sport_event_id = sport_event_info['id']
    sport_event_name = sport_event_info['name']
    sport_event_reminder = sport_event_info['reminder']

    print("\nReserving: {:s}(id={:d})".format(sport_event_name, sport_event_id))
    print("Notice: {:s}".format(sport_event_reminder))

    r = requests.get(url['sport_event_open_times'].format(sport_event_id), headers={'token': token}, cookies=cookies)
    # print(r.url)
    sport_event_open_times_info = r.json()
    # print(sport_event_open_times_info)
    sport_event_open_time_info = sport_event_open_times_info['data'][day]
    sport_event_open_time_day = sport_event_open_time_info['day']
    sport_event_open_time_weekname = sport_event_open_time_info['weekname']
    sport_event_open_time_status_text = sport_event_open_time_info['status_text']

    print("\nDay: {:s}, {:s}".format(sport_event_open_time_day, sport_event_open_time_weekname))
    print("Status: {:s}".format(sport_event_open_time_status_text))



    ### get hours info
    r = requests.get(url['sport_event_hours'].format(sport_event_id), cookies=cookies)
    # print(r.url)
    sport_event_hours_info = r.json()
    # print(sport_event_hours_info)
    sport_event_hours_info = sport_event_hours_info['data']
    # print(len(sport_event_hours_info)) # 15 for badminton, 7 for table tennis

    ### get hours ids
    hour_text_list, hour_id_list = [], []
    for data in sport_event_hours_info:
        hour_text_list.append('{:s}-{:s}'.format(data['begintime_text'], data['endtime_text']))
        hour_id_list.append(data['id'])
    # print(hour_text_list, hour_id_list)
    
    
    ### get fields info
    r = requests.get(url['sport_event_fields'].format(sport_event_id), cookies=cookies)
    # print(r.url)
    sport_event_fields_info = r.json()
    # print(sport_event_fields_info)
    sport_event_fields_info = sport_event_fields_info['data']
    # print(len(sport_event_fields_info)) # 12 for badminton, 13 for table tennis

    ### get fields ids
    field_text_list, field_id_list = [], []
    for _, data in sport_event_fields_info.items():
        field_text_list.append(data['name'])
        field_id_list.append(data['id'])
    # print(field_text_list, field_id_list)


    ### get booked info
    day_text = datetime.datetime.today() if day == 0 else datetime.datetime.today() + datetime.timedelta(days=1)
    day_text = day_text.strftime("%Y-%m-%d")
    r = requests.get(url['sport_schedule_booked'].format(sport_event_id, day_text), cookies=cookies)
    # print(r.url)
    sport_schedule_booked_info = r.json()
    available_resources = {}
    for book_key, book_value in sport_schedule_booked_info['data'].items():
        if book_value == 0:
            field_id, hour_id = book_key.split('-')
            available_resources.setdefault(field_id, []).append(hour_id)
    
    # print(available_resources)
    print("\nAvailable resources:")
    for f, h in available_resources.items():
        print(f)
        print(h)
    

    # print("\n===Argument Table===")
    print("\n(field id, field name):")
    for i in zip(field_id_list, field_text_list):
        print(i)
    print("\n(hour id, hour name):")
    for i in zip(hour_id_list, hour_text_list):
        print(i)
    
    i_want_field_id = input("Input field id:")
    i_want_hour_id_1 = [int(input("Input first hour id:"))]
    i_want_hour_id_2 = input("Input second hour id(press ENTER to skip):")
    if not i_want_hour_id_2 == '':
        i_want_hour_id_1.append(int(i_want_hour_id_2))
    # i_want_hour_id_2 = None if i_want_hour_id_2 == '' else int(i_want_hour_id_2)
    return sport_event_id, {i_want_field_id: i_want_hour_id_1}




def reserve(cookies, token, sport_event_id, i_want, day=1):

    # print(time.mktime(datetime.datetime.now().timetuple()), time.time())


    ### make the submit
    submit_day = datetime.datetime.today() if day == 0 else datetime.datetime.today() + datetime.timedelta(days=1)
    submit_day = submit_day.strftime("%Y-%m-%d")

    # scene = [{"day":"2022-05-12","fields":{"147":[328098,328099]}}]
    # scene=%5B%7B%22day%22%3A%222022-05-12%22%2C%22fields%22%3A%7B%22147%22%3A%5B328098%2C328099%5D%7D%7D%5D


    # scene = [{"day":"2022-05-12","fields":{"148":[328098]}}]
    # scene=%5B%7B%22day%22%3A%222022-05-12%22%2C%22fields%22%3A%7B%22148%22%3A%5B328098%5D%7D%7D%5D
    
    

    ### real wants
    scene = [{'day': submit_day, 'fields': i_want}]

    # scene = quote(json.dumps(scene))
    # scene = quote(json.dumps(scene).replace(' ', ''))
    scene = json.dumps(scene).replace(' ', '')
    payload = {'sport_events_id': sport_event_id, 'ordertype': 'makeappointment', 'paytype': 'bitpay', 'scene': scene}
    print("\n")
    print(payload)
    # print(json.dumps(payload))

    headers = {
        'token': token,
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
    }


    num_tries = 0
    html_data = None
    while True:
        r = requests.post(url['submit'], data=payload, headers=headers, cookies=cookies)
        num_tries += 1

        # print(dir(r.request))
        # print(r.request.headers)
        print(r.request.body)
    
        if r.status_code == requests.codes.ok:
            # print(r.text)
            submit_result = r.json()
            print("\n\n\n{:s}".format(submit_result['msg']))
            
            # data=<form id='alipaysubmit' name='wechatsubmit' action='https://pay.info.bit.edu.cn/pay/prepay' method='POST'><input type='hidden' name='productBody' value='乒乓球'/><input type='hidden' name='productDetail' value='中关村校区体育馆-乒乓球'/><input type='hidden' name='spbillCreateIp' value='114.246.192.109'/><input type='hidden' name='tenant' value='232001'/><input type='hidden' name='tenantRedirectUrl' value='http://gym.dazuiwl.cn/api/order/epay/type/notify/paytype/wechat'/><input type='hidden' name='tenantTradeNumber' value='20220516172802394648'/><input type='hidden' name='tenantUserCode' value='18044'/><input type='hidden' name='tenantUserName' value='oyoyo'/><input type='hidden' name='timestamp' value='1652693282'/><input type='hidden' name='totalFee' value='2000'/><input type='hidden' name='sign' value='58440A8E91F3C22957CD6DB050CE82FD'/><input type='submit' value='ok' style='display:none;'></form><script>document.forms['wechatsubmit'].submit();</script>
            html_data = submit_result['data']
            print(html_data)
            
            break
        elif r.status_code == requests.codes.bad_gateway:
            print("\n\n\n{:d}".format(r.status_code))
            print("Busy servers. Tried for {} times.".format(num_tries))
            # exit()
        else:
            print("\n\n\n{:d}".format(r.status_code))
            print("Login failed. Please try again.")
            exit()
    
    return html_data




def pay(html_data):
    # print(html_data)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_data)
    
    # os.system('python -m webbrowser -n ' + html_file)

    webbrowser.open(html_file)

    # html_file_abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), html_file)
    # print(html_file_abspath)
    # driver = webdriver.Chrome()
    # driver.get('file:///'+html_file_abspath)





if __name__ == '__main__':
    
    # parser = argparse.ArgumentParser(description='BIT gym script.')

    # parser.add_argument('-u', type=str, required=True, metavar='USERNAME', help="username (required)")
    # parser.add_argument('-p', type=str, required=True, metavar='PASSWORD', help="password (required)")
    # args = parser.parse_args()

    # login(args.u, args.p)
    action = int(input("0: preliminary, 1: reservation\nInput action:"))
    if action == 0:
        ### login and input wants
        u = input("Input student Id:")
        p = input("Input password:")
        # cookies, token = login('3120185492', 'OUYANGTONG1993')
        cookies, token, user_info = login(u, p)

        sport = int(input("\n0: table tennis, 1: badminton, 2:tennis\nInput sport:"))
        day = int(input("\n0: today, 1: tomorrow\nInput day:"))

        sport_event_id, i_want = wants(cookies, token, day=day, sport=sport)
        # print(sport_event_id, i_want)

        ### save login and wants
        if os.path.exists(config_file):
            os.remove(config_file)
        with open(config_file, 'w') as f:
            config = {
                'user_info': {
                    'verification_mobile': user_info['data']['verification']['mobile'],
                    'name': user_info['data']['name'],
                    'nickname': user_info['data']['nickname'],
                    'mobile': user_info['data']['mobile'],
                    'cookies': cookies,
                    'token': token
                },
                'wants': {
                    'sport_event_id': sport_event_id,
                    'i_want': i_want,
                    'day': day
                }
            }
            print("\n")
            print(config)
            json.dump(config, f, indent=4, ensure_ascii=False)
            print("\n\n\nLogin and your wants are saved in {:s}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)))
    elif action == 1:
        ### get login and wants
        if not os.path.exists(config_file):
            print("Login and input your wants first.")
            exit()
        with open(config_file, 'r') as f:
            config = json.load(f)


        if config['user_info']['verification_mobile']:
            print("\n\n\nHi, {:s}({:s}, {:s}).".format(config['user_info']['name'], config['user_info']['nickname'], config['user_info']['mobile']))
        else:
            print("\n\n\nHi, {:s}({:s}).".format(config['user_info']['name'], config['user_info']['nickname']))
        

        print("\n")
        print(config['wants'])


        ### reserve
        now_time = datetime.datetime.now()
        now_timestamp = time.mktime(now_time.timetuple())
        reserve_time = datetime.datetime(now_time.year, now_time.month, now_time.day, 7, 0, 1)
        reserve_timestamp = time.mktime(reserve_time.timetuple())


        print("\n")
        while now_timestamp < reserve_timestamp:
            print("\r{:s}".format(" "*40), end='')
            print("\rPlease wait for {:d} seconds".format(int(reserve_timestamp-now_timestamp)), end='')
            time.sleep(0.5)
            now_timestamp = time.mktime(datetime.datetime.now().timetuple())


        # day=0 for today, day=1 for tomorrow.
        # sport=[table tennis, badminton, tennis]
        # reserve(cookies, token, sport_event_id, i_want=i_want, day=day)
        html_data = reserve(config['user_info']['cookies'], config['user_info']['token'], config['wants']['sport_event_id'], i_want=config['wants']['i_want'], day=config['wants']['day'])
        if html_data:
            pay(html_data)
    
    else:
        print("Wrong input.")

