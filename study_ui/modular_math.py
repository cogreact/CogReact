from pywebio import start_server
from pywebio.session import register_thread
from pywebio.input import input, FLOAT, NUMBER, TEXT
from pywebio.input import select, radio, checkbox
from pywebio.output import output, put_text, put_scope, put_button, put_buttons, put_markdown, put_row, put_column, style, use_scope, put_processbar, set_processbar
from pywebio.output import popup, close_popup, toast
import argparse, time, random
from pywebio.platform import path_deploy, path_deploy_http
import os, datetime, json
from functools import partial
import numpy as np
import multiprocessing 
import threading

from feedback_strategy import None_Strategy, Static_Strategy, Random_Strategy, Rule_Strategy_Binary

class modular_math():
    def __init__(self, username, strategy_name):

        self.rule_config = {
            'ThresholdAccuracyUpper': None, 
            'ThresholdResponseTimeUpper': None, 
            'ThresholdResponseTimeDelta': 1, 
            'ThresholdPushNum': 3, 
            'ThresholdKeepNum': 2,
            'BufferSize': None,
        }
        self.username = username
        self.strategy_name = strategy_name
        
        self.num_1 = 0
        self.num_2 = 0
        self.num_3 = 0
        self.truth = 0
        self.math_question = ""
        self.user_data_path = 'userdatabase/' + username + '_math_modular_' + time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(int(time.time()))) + '/'
        self.math_question_output = output(put_text('Session 1: Exercise: Press Any Button to Start')) 
        
        self.math_count = 0
        self.user_accuracy = 0
        self.user_response_time = 0
        
        # self.button_choice = ['True Answer', 'False Answer']
        self.button_choice = [
            dict(label='True Answer', value = '0', color='success'),
            dict(label='False Answer', value = '1', color='danger') 
        ]
        self.math_generate_time = time.time()

        self.bar_num = 5
        self.time_pressure = output(put_text(datetime.datetime.now())) 
        self.bar_id = 0

        self.bar_present_flag = False
        self.bar_interval = 1

        if self.strategy_name == 'none':
            self.current_feedback = 0
        elif self.strategy_name == 'static':
            self.current_feedback = 1
        else:
            self.current_feedback = 0


        self.exercise_num = 1  # 10
        self.calibration_num = 1  # 100
        self.formal_math_num = 50 # 100
        self.answer_delay_time = 3 # 3
        self.rest_time_s1 = 1 # 60
        self.rest_time_s2 = 1 # 300
        self.question_interval = 5 # 30
        
        self.math_num = self.formal_math_num + self.calibration_num + 1 + self.exercise_num + 1

        self.user_response_time_overall_calib = []
        self.user_accuracy_overall_calib = []
        self.rest_button_lock = False

        self.math_calib_id = 0
        self.math_formal_id = 0
        self.user_result_calib_id = 0
        self.user_result_formal_id = 0

        self.user_attention = -1
        self.user_attention_time = -1
        self.user_anxiety = -1
        self.user_anxiety_time = -1

        
        self.attention_answered_flag = False
        self.anxiety_answered_flag = False
        self.question_atten_start = 0
        self.question_anxie_start = 0

    def judge_int(self,float_num):
        if float(int(float_num)) == float_num:
            return True
        else:
            return False

    def get_truth(self, n1, n2, n3):
        if self.judge_int(float(n1 - n2)/float(n3)) == True:
            return 1  
        else:
            return 0
    
    def math_digits_generator(self):
        num_1_unit = np.random.randint(1, 10) 
        num_1_ten = np.random.randint(2, 10) 
        num_1 = num_1_ten * 10 + num_1_unit             
    
        num_2_unit = np.random.randint(1,10)
        num_2_ten = np.random.randint(1, num_1_ten)
        num_2 = num_2_ten * 10 + num_2_unit

        num_3 = np.random.randint(3, 10)
        return num_1, num_2, num_3

    def math_question_generator(self):
        target_truth = np.random.randint(0, 2)
        self.num_1, self.num_2, self.num_3 = self.math_digits_generator()
        self.truth = self.get_truth(self.num_1, self.num_2, self.num_3)

        while self.truth != target_truth:
            self.num_1, self.num_2, self.num_3 = self.math_digits_generator()
            self.truth = self.get_truth(self.num_1, self.num_2, self.num_3)

        self.math_question = str(self.num_1) + " ≡ " + str(self.num_2) + " ( mod " + str(self.num_3) + " )"
        print(self.math_question, self.truth)
        self.save_math_question()

    def save_math_question(self):
        if os.path.exists(self.user_data_path) == False:
            os.mkdir(self.user_data_path)
        
        if self.math_count > self.calibration_num + self.exercise_num + 1:
            self.math_formal_id += 1
            with open(self.user_data_path + '/math_question.csv', 'a+') as outfile_math_1:
                outfile_math_1.write(str(int(self.math_formal_id)) + ',' + str(self.num_1) + "," + str(self.num_2) + "," + str(self.num_3) + "," + str(self.truth) + '\n')
        elif self.math_count > self.exercise_num:
            self.math_calib_id += 1
            with open(self.user_data_path + '/math_question_calib.csv', 'a+') as outfile_math_2:
                outfile_math_2.write(str(int(self.math_calib_id)) + ',' + str(self.num_1) + "," + str(self.num_2) + "," + str(self.num_3) + "," + str(self.truth) + '\n')
    
    def save_user_result(self):
        ''' data format: accu, resp time, attention, atten time, anxiety, anx time '''
        if os.path.exists(self.user_data_path) == False:
            os.mkdir(self.user_data_path)

        if self.math_count > self.calibration_num + self.exercise_num + 1:
            self.user_result_formal_id += 1
            with open(self.user_data_path + '/user_result.csv', 'a+') as outfile_user_result_1:
                outfile_user_result_1.write(str(int(self.user_result_formal_id)) + ',' + str(self.num_1) + "," + str(self.num_2) + "," + str(self.num_3) + "," + str(self.truth) + "," + str(self.current_feedback) + ',' + str(self.user_accuracy) + "," + str(self.user_response_time) + "," + str(self.user_attention) + "," + str(self.user_attention_time) + "," + str(self.user_anxiety) + "," + str(self.user_anxiety_time) + '\n')
        elif self.math_count > self.exercise_num:
            self.user_result_calib_id += 1
            with open(self.user_data_path + '/user_result_calib.csv', 'a+') as outfile_user_result_2:
                outfile_user_result_2.write(str(int(self.user_result_calib_id)) + ',' + str(self.num_1) + "," + str(self.num_2) + "," + str(self.num_3) + "," + str(self.truth) + "," + str(self.current_feedback) + ',' + str(self.user_accuracy) + "," + str(self.user_response_time) + "," + str(self.user_attention) + "," + str(self.user_attention_time) + "," + str(self.user_anxiety) + "," + str(self.user_anxiety_time) + '\n')

    def save_user_emotion(self):
        ''' data format: attention, atten time, anxiety, anx time '''
        if os.path.exists(self.user_data_path) == False:
            os.mkdir(self.user_data_path)

        with open(self.user_data_path + '/user_emotion.csv', 'a+') as outfile_user_emotion:
            outfile_user_emotion.write(str(self.user_attention) + "," + str(self.user_attention_time) + "," + str(self.user_anxiety) + "," + str(self.user_anxiety_time) + '\n')

    def btn_click_attention(self, btn_val):
        self.user_attention = float(btn_val)
        self.user_attention_time = time.time() - self.question_atten_start
        toast(str(btn_val))

    def btn_click_anxiety(self, btn_val):
        self.user_anxiety = float(btn_val)
        self.user_anxiety_time = time.time() - self.question_anxie_start
        toast(str(btn_val))
    
    def btn_click_submit_attention(self, btn_val):
        close_popup()
        time.sleep(1)
        popup('Questionnaire', [
            put_text('Rate your level of anxiety: 1-not anxious at all, 7-very anxious'),
            put_buttons(['1', '2', '3', '4', '5', '6', '7'], onclick = self.btn_click_anxiety),
            put_buttons(['submit'], onclick = self.btn_click_submit_anxiety)
        ])
        self.question_anxie_start = time.time()
    
    def btn_click_submit_anxiety(self, btn_val):
        self.save_user_emotion()
        close_popup()
        time.sleep(1)
        self.present_math()

    
    def present_math(self):
        if self.math_count == self.math_num:
            self.math_question_output.reset('You have finished the task')
            self.bar_present_flag = False
            self.math_count += 1
        else:
            self.math_count += 1
            self.math_question_generator()
            self.math_question_output.reset(self.math_question)
            self.math_generate_time = time.time()
            self.bar_id = 1
            if self.current_feedback == 0:
                self.bar_present_flag = False
            else:
                if self.current_feedback == 1:
                    self.bar_id = 0
                    self.bar_interval = 1
                else:
                    print('Wrong: ' + '*'*80)
                self.bar_present_flag = True

    def math_trial(self):
        print(self.username, ': math trial, self.math_count: ', self.math_count, '-'*80)
        if self.math_count == self.exercise_num:
            self.rest_button_lock = True
            if self.user_accuracy == 1:
                self.math_question_output.reset('Your answer is correct!')
            else:
                self.math_question_output.reset('Your answer is wrong!')
            time.sleep(self.answer_delay_time)
            self.math_question_output.reset('Have a rest for 30 seconds. \n DO NOT TURN OFF YOUR SCREEN OR SWITCH TO ANOTHER APPLICATION.')
            time.sleep(self.rest_time_s1)
            self.rest_button_lock = False
            self.math_count += 1
            self.math_question_output.reset('Session 2: Press Any Button to Continue') # check if the screen will turn off or affect the network connection
            print('\n Ready to Start Second session: self.math_count: ', self.math_count)
        elif self.math_count == self.calibration_num + self.exercise_num + 1:
            self.math_question_output.reset('Have a rest for 1 minute. \n DO NOT TURN OFF YOUR SCREEN OR SWITCH TO ANOTHER APPLICATION.')
            self.rest_button_lock = True
            time.sleep(self.rest_time_s2)
            self.rest_button_lock = False
            self.math_count += 1
            self.math_question_output.reset('Session 3: Press Any Button to Continue') # check if the screen will turn off or affect the network connection
            print('\n Ready to Start Third session: self.math_count: ', self.math_count)

        else:
            if self.math_count < self.exercise_num and self.math_count > 0:
                self.rest_button_lock = True
                if self.user_accuracy == 1:
                    self.math_question_output.reset('Your answer is correct!')
                else:
                    self.math_question_output.reset('Your answer is wrong!')
                time.sleep(self.answer_delay_time)
                self.rest_button_lock = False

            if (self.math_count - self.calibration_num - self.exercise_num - 2) % self.question_interval == 0 and self.math_count > self.calibration_num + self.exercise_num + 2:
                print('Pop Up: ', self.math_count)
                self.math_question_output.reset('waiting')
                self.bar_present_flag = False

                popup('Questionnaire', [
                    put_text('Rate your level of focus: 1-not focused at all, 7-very focused'),
                    put_buttons(['1', '2', '3', '4', '5', '6', '7'], onclick = self.btn_click_attention),
                    put_buttons(['submit'], onclick = self.btn_click_submit_attention)
                ])
                self.question_atten_start = time.time()
   
            else:
                self.present_math()
                


    def btn_click_math(self, btn_val):
        if self.math_count == self.calibration_num + self.exercise_num + 2:
            print('assign strategy')
            self.rule_config['BufferSize'] = self.calibration_num 
            self.rule_config['ThresholdAccuracyUpper'] = np.mean(self.user_accuracy_overall_calib)
            self.rule_config['ThresholdResponseTimeUpper'] = np.mean(self.user_response_time_overall_calib)
            print('self.rule_config[\'ThresholdAccuracyUpper\']: ', self.rule_config['ThresholdAccuracyUpper'])
            print('self.rule_config[\'ThresholdResponseTimeUpper\']: ', self.rule_config['ThresholdResponseTimeUpper'])
            if self.strategy_name == 'none':
                self.strategy = None_Strategy()
            elif self.strategy_name == 'static':
                self.strategy = Static_Strategy(static_pattern = 1)
            elif self.strategy_name == 'random':
                self.strategy = Random_Strategy(action_size = 2)
            elif self.strategy_name == 'rule':
                self.strategy = Rule_Strategy_Binary(self.rule_config)
            
            else:
                print('invalid feedback strategy')
                assert 1==0

        if self.math_count > 0 and self.math_count <= self.math_num and self.rest_button_lock == False and self.math_count != (self.exercise_num + 1) and self.math_count != (self.exercise_num + 1 + self.calibration_num + 1):
            # if self.button_choice.index(btn_val) * self.truth == 0:
            self.math_question_output.reset('waiting')

            if (int(btn_val) == 0 and self.truth == 1) or (int(btn_val) == 1 and self.truth == 0) :
                self.user_accuracy = 1.0
            else:
                self.user_accuracy = 0.0
            
            self.user_response_time = time.time() - self.math_generate_time
            print('int(btn_val), self.truth, self.user_accuracy, self.user_response_time: ', int(btn_val), self.truth, self.user_accuracy, self.user_response_time)

            if self.math_count > self.exercise_num:
                self.save_user_result()
            
            if self.math_count > self.calibration_num + self.exercise_num + 2:
                print('update data in session 3')
                state = [self.user_accuracy, self.user_response_time]
                done = False
                # filter: only consider response time in reasonable range (0.8,20) to provide feedback
                if self.user_response_time > 0.8 and self.user_response_time < 20:
                    self.strategy.update_state(state)
                    self.current_feedback = self.strategy.update_action()
                
            else:
                self.current_feedback = 0
                if self.math_count > self.exercise_num:
                    if self.user_response_time > 0.8 and self.user_response_time < 20:
                        print('update data in session 2')
                        self.user_response_time_overall_calib.append(self.user_response_time)
                        self.user_accuracy_overall_calib.append(self.user_accuracy)
                        print('self.user_response_time_overall_calib: ', self.user_response_time_overall_calib)
                        print('self.user_accuracy_overall_calib: ', self.user_accuracy_overall_calib)
        
        if self.math_count <= self.math_num and self.rest_button_lock == False:
            self.math_trial()

        elif self.rest_button_lock == False:
            self.strategy.train_flag = False
            self.strategy.save_replay_flag = False
            self.math_question_output.reset('You have finished the task')
            self.math_count += 1
            self.bar_present_flag = False

    def show_time(self):
        while True:
            if self.bar_present_flag == True:
                set_processbar('bar', self.bar_id / self.bar_num)
                time.sleep(self.bar_interval)
                if self.bar_id < 5:
                    self.bar_id += 1
                else:
                    self.bar_id = 0
                
            else:
                self.bar_id = 0
                set_processbar('bar', self.bar_id / self.bar_num)
                time.sleep(self.bar_interval)

    
    def main_run(self):
        t = threading.Thread(target=self.show_time)
        register_thread(t)
        put_markdown('## Modular Math Task')
        
        put_processbar('bar')

        t.start()  # run `show_time()` in background

        put_column([
            None,None,None,None,None,None,None,None,
            put_row([None, self.math_question_output], size = '50px, 100%').style('font-size: 30px'),
            None,None,None,None,None,None,None,None,
            put_row([None, put_buttons(self.button_choice, onclick = self.btn_click_math)], size = '50px, 100%')
            # put_row([None, put_buttons(self.button_choice, onclick = self.btn_click_math, link_style = True)]).style('font-size: 100px')
        ])
        
        




    





