import sys  # sys нужен для передачи argv в QApplication
import os
import re
import pandas as pd
import numpy as np
from datetime import datetime, date, time
import time as ttime

import  subprocess
import logging
import paramiko
import socket
import json

from .my_ssh import ssh_conf
from .global_report_24 import rep_from_test_res  # файл с функциями построения отчета
from .test_json_to_txt import my_reports  # файл с функциями построения форматированного текстового отчета

class ExampleApp():

#    server_directory = '/home/murd/buf/ft_userdata/'
#    server_directory = '/root/application'
#    server_strategy_directory = '/user_data/strategies/'
#    server_backtests_directory = '/user_data/backtest_results/'
#    server_reports_directory = '/reports/'
#    server_user_directory = 'My_backtest_results' #'admin_dir'
#    client_directory = ''
#    reports_directory = './reports/'

    # Информация о сервере, имя хоста (IP-адрес), номер порта, имя пользователя и пароль

#    hostname = "172.18.90.46"
#    port = 2222
#    username = "murd"
#    password = "Ambaloid!"

#    hostname = "gate.controller.cloudlets.zone"
#    hostname = "node7441-ft-stable.node.cloudlets.zone"
#    hostname = "212.127.94.1"
#    port = 3022
#    username = "7441-732"

    hostname = ssh_conf.hostname
    port = ssh_conf.port
    username = ssh_conf.username

    server_directory = ssh_conf.server_directory
    server_strategy_directory = ssh_conf.server_strategy_directory
    server_backtests_directory = ssh_conf.server_backtests_directory
    server_reports_directory = ssh_conf.server_reports_directory
    local_reports_directory = ssh_conf.local_reports_directory
    server_user_directory = ssh_conf.server_user_directory
    client_directory = ssh_conf.client_directory    

    list_info = []
    
    def get_ssh_connect(self, show_info = True):

        logger = paramiko.util.logging.getLogger()
        hdlr = logging.FileHandler('app.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)

         # Создать объект SSH
        if show_info: 
            self.list_info.append("Runing SSH...")
            self.list_info.append("Host name: " + self.hostname )
            self.list_info.append("Port: " + str(self.port))
        try:        
            client = paramiko.SSHClient()
         # Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.RSAKey.from_private_key_file('RSA_private_1.txt')
         # подключиться к серверу
        
#            client.connect(self.hostname, self.port, self.username, self.password, compress=True)
            client.connect(self.hostname, self.port, self.username, pkey=private_key, timeout=3, disabled_algorithms=dict(pubkeys=['rsa-sha2-256', 'rsa-sha2-512']))
                        
        except Exception as e:
            logging.debug(e)
            self.list_info.append('Error connection to server: ' + str (e) )
            #self.listInfo.addItem("Invalid login/password!")
            self.list_info.append('________________________________________')
            return 'error'
            
        else:
            if show_info:
                self.list_info.append("Connected to server!" + '\n')
                self.list_info.append('________________________________________' + '\n')

        return client

    def get_sftp_connect(self):

        logger = paramiko.util.logging.getLogger()
        hdlr = logging.FileHandler('app.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)

        try:
#        self.server_directory ='/home/murd/buf/ft_userdata'
            private_key = paramiko.RSAKey.from_private_key_file('RSA_private_1.txt')
            transport = paramiko.Transport((self.hostname, self.port))
            transport.connect(username = self.username, pkey = private_key)
        
            sftp = paramiko.SFTPClient.from_transport(transport)    
            
        except Exception as e:
            logging.debug(e)
            self.list_info.append('Error connection to server (sftp): ' + str (e) + '\n')
            #self.listInfo.addItem("Invalid login/password!")
            self.list_info.append('________________________________________' + '\n')
            return 'error'
            
        else:
            self.list_info.append("Connected to server (sftp)!" + '\n')
            self.list_info.append('________________________________________' + '\n')

        return sftp

    def connect_ssh(self):
        
        # На случай, если в списке уже есть элементы
        list_backtest = []
        list_strategies = []
        
        max_bytes=60000

#        self.username = self.lineEdit_Login.text()
#        self.password = self.lineEdit_Password.text()
       
        
        client = self.get_ssh_connect() #создаем ssh-подключение
        if client != 'error':
            sftp_client = client.open_sftp()
            current_dir = sftp_client.getcwd()
        else:
            return list_strategies, list_backtest
        
        #Проверяем наличие, на сервере, полльзователького каталога, если такго не существует - создаем
        try:
            sftp_attributes = sftp_client.stat(self.server_directory + self.server_backtests_directory+self.server_user_directory)
        except Exception as e:
#            self.listInfo.addItem('Error connection to server: ' + str (e))
            sftp_client.mkdir(self.server_directory + self.server_backtests_directory+self.server_user_directory)
            self.list_info.append("Created user directory: " + self.server_user_directory + '\n')

        try:
            sftp_attributes = sftp_client.stat(self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory)
        except Exception as e:
            sftp_client.mkdir(self.server_directory + self.server_backtests_directory + self.server_user_directory + self.server_reports_directory)
            self.list_info.append("Created user report directory: " + self.server_user_directory + self.server_reports_directory + '\n')

         # Выполнить команду linux
        command = 'ls /' + self.server_directory + self.server_strategy_directory
        
        stdin, stdout, stderr = client.exec_command(command)

        for file_name in stdout:  # для каждого файла в директории
            file_name = file_name.strip('\n')
            splited_str = file_name.split('.')
            if len(splited_str) == 2:
               if splited_str[1] == 'py':
                  splited_str2 = splited_str[0].split('_')
                  if splited_str2[0] in ['min']:
                     list_strategies.append(file_name) # добавить файл в listStrategies


        command = 'ls /' + self.server_directory + self.server_backtests_directory + self.server_user_directory
        
        stdin, stdout, stderr = client.exec_command(command)
        for file_name in stdout:  # для каждого файла в директории
            file_name = file_name.strip('\n')
            if file_name != '.last_result.json':
               splited_str = file_name.split('.')
               if len(splited_str) == 2:
                  if splited_str[1] == 'json': 
                     list_backtest.append(file_name)   # добавить файл в listBtResults

        
        sftp_client.close()
        client.close()

        return list_strategies, list_backtest
            
    def get_strategy(self, f_name: str):

        client = self.get_ssh_connect(show_info = False) #создаем ssh-подключение
        sftp_client = client.open_sftp()
        remote_file = sftp_client.open (self.server_directory + self.server_strategy_directory + f_name) # Путь к файлу
        try:
            strategy_name = 'none'
            for line in remote_file:
                line = line.strip()
                if ('class' in line) and ('IStrategy' in line):
                    pars_str1 = line.split()
                    pars_str = pars_str1[1].split('(') #re.split(' |()', line)
                    strategy_name = pars_str[0]
                    
                    self.list_info.append("Strategy name: ")
                    self.list_info.append(strategy_name)
                    self.list_info.append('________________________________________')
                    
        finally:
            remote_file.close()

        client.close()
        
        return strategy_name

    def run_report(self, backtest_file_name, mode, user_name):
        self.server_user_directory = user_name
        my_txt_rep = my_reports()   #создаем объект нашего собственного класса my_reports()
        
        my_rep = rep_from_test_res() #создаем объект нашего собственного класса rep_from_test_res()
        if mode == 'local':
            if not os.path.exists("./reports/" + user_name + "/"):
                os.mkdir("reports/" + user_name)
                os.mkdir("reports/" + user_name + "/txt")
                os.mkdir("reports/" + user_name + "/xlsx")
                self.list_info.append("Created directory: /reports/" + user_name)

        client = self.get_ssh_connect() #создаем ssh-подключение
        if client != 'error':
            sftp = client.open_sftp()
            remote_file = sftp.open ('/' + self.server_directory + self.server_backtests_directory +self.server_user_directory + '/' + backtest_file_name, mode = 'r') # Путь к файлу
            json_obj = json.loads(remote_file.read())
            
            self.list_info.append("Creating report, please wait... ")

            buf_str = backtest_file_name.split('.')
            if mode == 'local':
              res_report = my_txt_rep.json_to_txt(json_obj, remote_file, mode, self.local_reports_directory + user_name + '/txt/', backtest_file_name)
            else:
                remote_file = sftp.open ('/' + self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory +buf_str[0] + '.txt', mode = 'w') # Путь к файлу
                res_report = my_txt_rep.json_to_txt(json_obj, remote_file, mode, self.server_reports_directory, backtest_file_name)
            self.list_info.append("Created report: ")
            self.list_info.append(buf_str[0] + '.txt')

            res_report = my_rep.get_report(json_obj, mode, user_name, self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory, backtest_file_name)
            if res_report == "no_trades":
                self.list_info.append("Created report error: No trades in test results!")
            else:
                self.list_info.append("Created report: ")
                self.list_info.append(backtest_file_name.split('.')[0]+'_t1.xlsx')
            self.list_info.append('________________________________________')
            rep_done =True
            sftp.close()
        else:
            return
        

        return rep_done

    def run_backtest(self, user_strategy_settings, user_name):
        self.server_user_directory = user_name
        buf_str = self.get_strategy(user_strategy_settings["f_strategies"])
        file_config = 'usr_' + buf_str + '_config.py'
        max_bytes=160000
        short_pause=1
        long_pause=5
        
        if buf_str != 'none':
            datadir = " --datadir user_data/data/binance "
            export = " --export trades "
            config = " --config user_data/config_p" + user_strategy_settings["f_parts"] + ".json "
            export_filename = " --export-filename user_data/backtest_results/" + self.server_user_directory + "/bc_" + str(user_strategy_settings["f_series_len"]) +'_p' + user_strategy_settings["f_parts"]+ '_' + buf_str + '.json'

            strategy = " -s "+ buf_str
            
            run_str = "docker-compose run --rm freqtrade backtesting " + datadir+export+ config+ export_filename+strategy
            
            self.list_info.append('Command line for run test:')
            self.list_info.append(run_str)
            self.list_info.append('________________________________________')
        else:
            self.list_info.append('Strategy name not found!!!')
            self.list_info.append('________________________________________')

        # Minimal ROI designed for the strategy.
        not_first = False
        buf_str = '    minimal_roi = { "'
        if user_strategy_settings["f_min_roi_value1"] > 0:
            buf_str += str(user_strategy_settings["f_min_roi_time1"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value1"])
            not_first = True
        if user_strategy_settings["f_min_roi_value2"] > 0:
            if not_first:
                buf_str += ', "'
            buf_str += str(user_strategy_settings["f_min_roi_time2"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value2"])
            not_first = True
        if user_strategy_settings["f_min_roi_value3"] > 0:
            if not_first:
                buf_str += ', "'
            buf_str += str(user_strategy_settings["f_min_roi_time3"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value3"])
            not_first = True
        if user_strategy_settings["f_min_roi_value4"] > 0:
            if not_first:
                buf_str += ', "'
            buf_str += str(user_strategy_settings["f_min_roi_time4"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value4"])

        buf_str += '}'
        strategy_settings = pd.Series([buf_str])

        buf_str = '    arg_N =  ' + str(user_strategy_settings["f_series_len"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        #arg_X=0
        
        buf_str = '    arg_R =  ' + str(user_strategy_settings["f_persent_same"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        #- arg_P % price increase in arg_N candles
        buf_str = '    arg_P =  ' + str(user_strategy_settings["f_price_inc"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)       
           
        #- arg_MR % movement ROI
        buf_str = '    arg_MR =  ' + self.normalyze_percents(user_strategy_settings["f_movement_roi"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # Optimal stoploss designed for the strategy.
        buf_str = '    stoploss = -' + self.normalyze_percents(user_strategy_settings["f_stop_loss"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # Optimal time-depended stoploss designed for the strategy.
        buf_str = '    my_stoploss = np.array([' + str(user_strategy_settings["f_my_stop_loss_time"]) + ', -'+ self.normalyze_percents(user_strategy_settings["f_my_stop_loss_value"]) + '])'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True) 

        #(S = desired Stop-Loss Value)
        buf_str = '    arg_stoploss =  ' + self.normalyze_percents(user_strategy_settings["f_des_stop_loss"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        
#        with open(file_config, 'w') as out_file:
#            out_file.write('#  '+datetime.now().strftime('%Y-%m-%d / %H:%M:%S')+'\n \n')
#            out_file.write('import numpy as np \n')
#            out_file.write('class config_strategy(): \n')
            
            # сохранить файл конфигурации тестируемой стратегии в каталоге пользователя
#            for buf_str in strategy_settings:
#                out_file.write(buf_str+'\n')

#        out_file.close()

        client = self.get_ssh_connect() #создаем ssh-подключение
        if client != 'error':
            sftp_client = client.open_sftp()
            remote_file = sftp_client.open ('/' + self.server_directory + self.server_strategy_directory + file_config, mode = 'w') # Путь к файлу
            try:
                remote_file.write('#  '+datetime.now().strftime('%Y-%m-%d / %H:%M:%S')+'\n \n')
                remote_file.write('import numpy as np \n')
                remote_file.write('class config_strategy(): \n')
            
            # сохранить файл конфигурации тестируемой стратегии в каталоге пользователя
                for buf_str in strategy_settings:
                    remote_file.write(buf_str+'\n')

            finally:
                remote_file.close()
            #загрузить файл конфигурации тестируемой стратегии на сервер
#            sftp.put("./" + file_config, '/' + self.server_directory + self.server_strategy_directory + file_config)
                sftp_client.close()

        else:
            return

        self.list_info.append('Settings for current test:')
        for buf_str in strategy_settings:
            self.list_info.append(buf_str)

        self.list_info.append('Saved in config file: ' + file_config)   
        self.list_info.append('________________________________________')


        client = self.get_ssh_connect()

        time_1 = ttime.time()
        time_interval = 0
                
        with client.invoke_shell() as ssh:
            ssh.recv(max_bytes)
            self.list_info.append('________________________________________')

            command = "cd /" + self.server_directory
            ssh.send(f"{command}\n")
            ttime.sleep(short_pause)

            command = "source freqtrade/.env/bin/activate"
            ssh.send(f"{command}\n")
            ttime.sleep(short_pause)

            part = ssh.recv(max_bytes).decode("utf-8")
            self.list_info.append(part) 

            commands = [run_str]  # команда(строка) для запуска бектеста с заданными параметрами
            result = {}
            wating_test_result = 300
            pb_step = wating_test_result/100
#            self.timer.start(round(pb_step*1000))
            for command_ in commands:
                ssh.send(f"{command_}\n")
                ssh.settimeout(1)    #пауза после отправки команды, чтобы дать появиться сопутствующему тексту консоли
                  
                output = ""

                while (time_interval < 7) and (not("Closing async ccxt session" in part)):
                    time_2 = ttime.time()
                    time_interval = (time_2 - time_1)/60
#                    QtWidgets.QApplication.processEvents()
                    try:
                        part = ssh.recv(max_bytes).decode("utf-8")
                        self.list_info.append(part)
                        ttime.sleep(0.5)
                        
                    except socket.timeout:
                        continue

            self.list_info.append('________________________________________')
#            self.reset_pb_test()

            client.close()

    def normalyze_percents(self, num: str):
       buf = float(num)/100
       str_num = str(buf)
       return str_num

    def param_of_cur_strategy(self, user_strategy_settings):
        
           buf_str = self.get_strategy(user_strategy_settings["f_strategies"])
           buf_str = buf_str + '_config.py'
#           user_strategy_settings["f_reports"] = os.getcwd()
           f_path = './crypto_back/templates/conf_strategies/' + buf_str
            
           if os.path.exists(f_path):
               with open(f_path, 'r') as f:
                   user_strategy_settings["f_parts"] = list('1')
                   for line in f:
                       line = line.strip()
                       if ('arg_N' in line):
                           pars_str = line.split('=')
                           user_strategy_settings["f_series_len"] = pars_str[1].strip()
                           
                       if ('arg_R' in line):
                           pars_str = line.split('=')
                           user_strategy_settings["f_persent_same"] = pars_str[1].strip()

                       if ('arg_P' in line):
                           pars_str = line.split('=')
                           user_strategy_settings["f_price_inc"] = pars_str[1].strip()

                       if ('arg_MR' in line):
                           pars_str = line.split('=')
                           buf_str = str(float(pars_str[1].strip())*100)
                           user_strategy_settings["f_movement_roi"] = buf_str

                       if ('stoploss' in line):
                           pars_str = line.split('=')
                           if pars_str[0].strip() == 'stoploss' :
                               buf_str = str(round(abs(float(pars_str[1].strip())*100), 3))
                               user_strategy_settings["f_stop_loss"] = buf_str

                       if ('arg_stoploss' in line):
                           pars_str = line.split('=')
                           buf_str = str(round(float(pars_str[1].strip())*100, 3))
                           user_strategy_settings["f_des_stop_loss"] = buf_str

                       if ('my_stoploss' in line):
                           pars_str = line.split('=')
                           pars_str = pars_str[1].split('[')
                           pars_str = pars_str[1].split(']')
                           pars_str = pars_str[0].split(',')
                           user_strategy_settings["f_my_stop_loss_time"] = pars_str[0].strip()
                           buf_str = str(round(abs(float(pars_str[1].strip())*100), 3))
                           user_strategy_settings["f_my_stop_loss_value"] = buf_str

                       if ('minimal_roi' in line):
                           roi = []
                           pars_str = line.split('=')
                           buf_str = pars_str[1].strip().strip('{}')
                           pars_str = buf_str.strip().split(',')
                           
                           for i in range(len(pars_str)):
                               pars_str1 = pars_str[len(pars_str)-1 - i].strip().split(':')

                               roi_val = str(round(abs(float(pars_str1[1].strip())*100), 3))
                               roi_time = pars_str1[0].strip('""')

                               user_strategy_settings["f_min_roi_time1"] = 0
                               user_strategy_settings["f_min_roi_value1"] = 0
                               user_strategy_settings["f_min_roi_time2"] = 24
                               user_strategy_settings["f_min_roi_value2"] = 0
                               user_strategy_settings["f_min_roi_time3"] = 30
                               user_strategy_settings["f_min_roi_value3"] = 0
                               user_strategy_settings["f_min_roi_time4"] = 60
                               user_strategy_settings["f_min_roi_value4"] = 0

                               if roi_time == '0':
                                   user_strategy_settings["f_min_roi_value1"] = roi_val

                               if roi_time == '24':
                                   user_strategy_settings["f_min_roi_value2"] = roi_val

                               if roi_time == '30':
                                   user_strategy_settings["f_min_roi_value3"] = roi_val

                               if roi_time == '60':
                                   user_strategy_settings["f_min_roi_value4"] = roi_val

               
               f.close()
           else:
              user_strategy_settings["f_reports"] += f_path
           return user_strategy_settings

def main():
    ui_utils = ExampleApp()  # Создаём объект класса ExampleApp
#    ui_utils.load_ssh_my_config() # load ssh_my_config file
    l1, l2 = ui_utils.connect_ssh()
    print("Host: {0}  Port: {1}  UserName: {2}".format(ui_utils.hostname, ui_utils.port, ui_utils.username))
    for b in range(len(ui_utils.list_info)):
    	print(ui_utils.list_info[b])
    print(l1, l2)
    print(os.getcwd())
 
#    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()    

