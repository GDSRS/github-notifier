import requests
import json
from datetime import datetime
import subprocess
import time
import sys
import os
import gi
import getpass
gi.require_version('Notify', '0.7')
from gi.repository import Notify

url = 'https://api.github.com/repos/'

organization_or_user = sys.argv[1]
repository = sys.argv[2]
branch = sys.argv[3]

def get_time(response):
    time = datetime.strptime(response['commit']['commit']['author']['date'],'%Y-%m-%dT%H:%M:%SZ')
    return time

def make_request(url,headers=None):
    response = requests.get(url,headers)
    return response.json()

def sendmessage(message):
    subprocess.Popen(['notify-send', message])
    return

def notify(title,time):#ver se tem como setar um tempo
    Notify.init("myapp_name")
    n = Notify.Notification.new(title, str(time), os.getcwd()+"/teste.png")
    n.show()

def download_img(image_url):
    image = requests.get(image_url)
    with  open('teste.png','wb') as f:
        f.write(image.content)

def get_commit_info(request):
    download_img(request['commit']['author']['avatar_url'])
    message =  request['commit']['commit']['message']
    return message

def store_token(token):
    with open('token.txt','w') as f:
        f.write(token)

def acquire_token():
    try:
        lines = [line.rstrip('\n') for line in open('token.txt')]
        return lines[0]
    except FileNotFoundError:
        return acquire_token_from_web()


def acquire_token_from_web():
    base_url = 'https://api.github.com/'
    base_url += 'authorizations'
    username = input('username: ')
    password = getpass.getpass('password: ')
    response = requests.post(base_url,auth=(username,password),data=json.dumps({'note':'github notifier'}))
    print(response)
    response = response.json()
    print(response)
    token = response['token']
    return token

token = acquire_token()
headers = {'Authorization': 'token '+token}

url = url+organization_or_user+"/"+repository+"/branches/"+branch
response = make_request(url,headers)
old_time = get_time(response)

while(True):
    time.sleep(300)
    request = make_request(url,headers)
    new_time = get_time(request)
    if new_time > old_time:
        message = get_commit_info(request)
        notify(message,new_time)
        old_time == new_time
    else:
        print("sleep " + str(datetime.now()))
