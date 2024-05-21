from pywebio import start_server, config
from pywebio.session import register_thread
from pywebio.input import input, FLOAT, NUMBER, TEXT
from pywebio.input import select
from pywebio.output import put_text, put_html, put_scope, style, put_link, put_markdown, use_scope
import argparse, time, datetime
from pywebio.platform import path_deploy, path_deploy_http
from os import path
import threading
import numpy as np
import json

from modular_math import modular_math

# install list: pywebio, numpy

@config(theme="minty")
def timecare():
    with open('usercode_demo.json', 'r') as fjson:
        usercode_lib = json.load(fjson)
    put_text('Welcome to the study! \n')
    username = input("Your Invitation Code：", type=TEXT)
    print('username: ',username)
    
    
    if username not in usercode_lib.keys():
        put_text('You are not invited to join in this study.')
    else:
        studytype = select(label='Select Your Study Type', options = ['Task 1: Modular Math'])
        print('studytype: ',studytype)
        strategy = usercode_lib[username]
        if studytype == 'Task 1: Modular Math':
            modular_math_task = modular_math(username = username, strategy_name = strategy)
            modular_math_task.main_run()
        else:
            put_text('Please return and only select task 1.')


    

if __name__ == '__main__':
    start_server(timecare, port=80, remote_access = True)



