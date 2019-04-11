'''
Description:
Raise actionlist for different types.
By API: Top Up money/pass, Autoload
By Web: Block, Debit
    
Install:
pip install -U pytest selenium pytest-html pytest-selenium

References:
https://pytest-selenium.readthedocs.io/en/latest/user_guide.html
'''
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import logging
from logging.handlers import RotatingFileHandler
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By       
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import os
import ipdb
from config_data import *
import ast
import inspect
import random

# Global bearer access_token, empty by default while the bearer API has never been called.
bearer_access_token = ''


# *** OpCo Web automation parameters ***
# explicit wait time after loading a new page to check page match.
TIMEWAIT_PAGE_LOAD = 5
LOG_LEVEL = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Assume project structure as below:
# Scripts - python scripts
# Logs - logs
# run.bat - batch script to run

# root_path is parent folder of Scripts folder (one level up)
root_path = os.path.dirname( os.path.dirname(os.path.realpath(__file__)) )


common_formatter = logging.Formatter('%(asctime)s %(levelname)s line-%(lineno)d: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
# Note: To create multiple log files, must use different logger name.
def setup_logger(log_file, level=logging.INFO, name='', formatter=common_formatter):
    '''Function setup as many loggers as you want'''
    handler = logging.FileHandler(log_file,mode='w') # default mode is append
    # Or use a rotating file handler
    # handler = RotatingFileHandler(log_file,maxBytes=1024, backupCount=5)          
    handler.setFormatter(formatter)    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)    
    return logger   
    
# default debug logger 
debug_log_filename = root_path + os.sep + 'Logs' + os.sep + 'debug.log'
log = setup_logger(debug_log_filename, LOG_LEVEL,'log')

# logger for API outputs
api_formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
api_outputs_filename = root_path + os.sep + 'Logs' + os.sep + 'api_outputs.log'
log_api = setup_logger(api_outputs_filename, LOG_LEVEL,'log_api',formatter = api_formatter)

# pretty print Restful request to API log
# argument is request object 
def pretty_print_request(request):
    '''
    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    '''
    log_api.critical('{}\n{}\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        request.body)
        )

# pretty print Restful request to API log
# argument is response object         
def pretty_print_response(response):
    '''
    Pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    '''
    log_api.critical('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text
        ))        

        
# argument is request object
# display body in json format explicitly with expected indent. Actually most of the time it is not very necessary because body is formatted in pretty print way.    
def pretty_print_request_json(request):
    '''
    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    '''
    # ipdb.set_trace()
    log_api.critical('{}\n{}\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        json.dumps(ast.literal_eval(request.body),indent=4))
        )
        
# argument is response object 
# display body in json format explicitly with expected indent. Actually most of the time it is not very necessary because body is formatted in pretty print way.    
def pretty_print_response_json(response):
    '''
    Pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    '''
    log_api.critical('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        json.dumps(response.json(),indent=4)
        ))

class TestAPI:
    '''
    Test Restful HTTP API examples. 
    ''' 
    def setup_class(cls):
        print('Todo: To load test data.')
        # Use variable for data
    # Note: it will automatically to add quotes ('') to variable values in the dictionary, 'variable_1' instead of variable_1.
    def use_variable_in_data():
        var_value1 = 'variable_1'
        payload = {'key1': var_value1, 'key2': 'value2'}
        test_headers = {'Content-Type': "application/json" }
        r2 = requests.post('http://httpbin.org/post', data = str(payload), headers = test_headers) 
        ''' HTTP body is like this:
        {'key1': 'variable_1', 'key2': 'value2'}
        '''        
    # use_variable_in_data()
    
    def url_params():
        #To put parameters in request url
        payload = {'key1': 'value1', 'key2': 'value2'} 
        r2 = requests.get('http://www.petersvpn.com', params = payload)
        # full request:  http://www.petersvpn.com/?key1=value1&key2=value2

    # authentication
    # test response data
    def auth_n_respone_json():
        r3 = requests.get('https://api.github.com/user', auth=('peter.jp.xie@gmail.com', 'peter_0909'))
        # print ('Resp body text:\r\n' + r3.text) # raw text format
        print ('\nResp body json format:')
        print (r3.json()) # Note: It returns a dictionary object, though it is called json
        print ('\nResp body json pretty print format:')
        print (json.dumps(r3.json(),indent=4))
        print ('\nhtml_url is: ' + r3.json()['html_url'] )
   
class TestCPortalAL_API:
    '''
    Test customer portal actionlist by API. 
    ''' 
    def setup_class(cls):
        print('Todo: To load test data.')
    

    def post(self,url,data,headers={},verify=False,amend_headers=True):
        '''
        common request post function with below features, which you only need to take care of url and body data:
            - get bearer token if none
            - append common headers
            - print request and response in API log file
            - arguments are the same as requests.post
        '''
        # get bear token if none
        global bearer_access_token
        if bearer_access_token == '':
            self.get_bearer_token()
        
        # append common headers if none
        headers_new = headers
        if amend_headers == True:
            # headers = {'Content-Type':r'application/json','Authorization': 'Bearer ' + bearer_access_token}
            if not headers_new.__contains__('Content-Type'):
                headers_new['Content-Type']=r'application/json'
            if not headers_new.__contains__('Authorization'):
                headers_new['Authorization']='Bearer ' + bearer_access_token
                
        # send post request
        resp = requests.post(url, data = data, headers = headers_new, verify = verify)
        
        # pretty request and response into API log file
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)
        
        # This return caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]        
        if resp.status_code != 200:
            log.error('%s failed with response code %s.' %(caller_func_name,resp.status_code))
            return None
        return resp.json()
        
    def get_bearer_token(self):
        'Token value for 2 hours, enough for 1 round of tests.'
        log.info('Calling get_bearer_token.')
        url='https://%s/auth/oauth/v2/token' % api_server_url
        headers = {'content-type':r'application/x-www-form-urlencoded'}
        payload = {'client_id': ClientID, 'client_secret':ClientSecret, 'grant_type':'client_credentials'}  
        resp = requests.post(url, data = payload, headers = headers, verify=False)
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)
        try:
            global bearer_access_token
            bearer_access_token = resp.json()['access_token']
            log.info('Got bearer_access_token:' + str(bearer_access_token))
            return True
        # except KeyError:
        except:
            log.error('Failed to parse bearer token from response.')
            return False
            
    def myki_card_enquiry(self, mykiCardNumber_):
        '''
        Return json format of card enquiry
        '''
        log.info('Calling myki_card_enquiry %s' % mykiCardNumber_) 
        
        url='https://%s/%s/ma/card/enquiry' % (api_server_url,env_id)
        
        payload = {  
        "source" : "PTVWebsite",
        "Card" : [{	"mykiCardNumber" : mykiCardNumber_ }]
        } 

        # headers are taken care by self.post()
        # headers = {'Content-Type':r'application/json','Authorization': 'Bearer ' + bearer_access_token}
        
        # return self.post(url, data = json.dumps(payload,indent=4), headers = headers)
        return self.post(url, data = json.dumps(payload,indent=4) )

    def user_auth(self,username,password):
        log.info('Calling user_auth %s / %s .' % (username,password))
        url='https://%s/%s/im/user/authenticate' % (api_server_url,env_id)        
        payload = {  
        "username": username,
        "password": password
        } 
        return self.post(url, data = json.dumps(payload,indent=4))
        
    def myki_account_enquiry(self,username,password):
        log.info('Calling myki_account_enquiry %s / %s .' % (username,password))
        
        #get account JwtToken
        ret=self.user_auth(username,password)
        if ret == None:
            log.error('myki_account_enquiry failed because user auth failed with non-200 response %s / %s.' %(username,password) )
            return None
        elif ret["Response"]["message"] != "Success":
            log.error('myki_account_enquiry failed because user auth failed with Fail message %s / %s.' %(username,password) )
            return None
        else:
            JwtToken = ret["Response"]["accessToken"]
        
        url='https://%s/%s/ma/account/enquiry' % (api_server_url,env_id)
        headers = {'Content-Type':r'application/json',
        'Authorization': 'Bearer ' + bearer_access_token, 
        'AccessToken': JwtToken}
        
        payload = {  
        "source" : "PTVWebsite"
        } 

        return self.post(url, data = json.dumps(payload,indent=4), headers = headers)

    def test_func(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        #self.get_bearer_token()
        # self.myki_card_enquiry('308425030449522')
        #ret = self.user_auth('03044952','keane*12')
        # self.myki_account_enquiry('03044952','keane*12')
        # if ret == None:
        #     print('Auth failed.')
    
    def get_unique_order_no(self):
        now_sec = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str=str(random.choice(range(100)))
        return 'AUT' + now_sec + random_str
    
    def test_card_enquiry(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        
        #return if cards not defined
        try: CARD_ENQUIRY_CARDS
        except NameError: return
        
        for card in CARD_ENQUIRY_CARDS:
            self.myki_card_enquiry(card)
    
    def test_topup_money(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        
        #return if cards not defined
        try: TOPUP_MONEY_CARDS
        except NameError: return
        
        # TOPUP_MONEY_CARDS=['308425030410763','308425030415820']
        # Failed cards and responding errors. Format card:error 
        failed_cards = {}
        
        for card in TOPUP_MONEY_CARDS:
            # get card details
            ret=self.myki_card_enquiry(card)
            if ret is None:
                log.error('myki_card_enquiry of %s failed with wrong response code.' % card)              
                failed_cards[card] = 'card enquiry failed'
            else:  
                try:
                    #ipdb.set_trace()
                    mykiCardStatus_ = ret["Response"]["Result"]["Card"]["mykiCardStatus"]
                    mykiCardExpiryDate_ = ret["Response"]["Result"]["Card"]["mykiCardExpiryDate"]
                    
                    orderRefNo = self.get_unique_order_no()
                    payload = {
                        "source": "PTVWebsite",
                        "Card": {
                            "mykiCardNumber": card,
                            "mykiCardStatus": mykiCardStatus_,
                            "mykiCardExpiryDate": mykiCardExpiryDate_
                        },
                        "Order": {
                            "orderReferenceNumber": orderRefNo,
                            "orderSequenceNumber": 1,
                            "amount": Topup_Money_Amount
                        },
                        "Contact": {
                            "preferredReminder": "Email",
                            "email": Notification_Email,
                            "notification": True, # Note it is converted to json dump, it will convert to json boolean true (lower case) automatically.
                            "reminderValue": Notification_Email
                        }
                    }
                    url='https://%s/%s/ma/card/topup/mykimoney' % (api_server_url,env_id)
                    ret_topup = self.post(url, data = json.dumps(payload,indent=4))
                    # check if top up is successful
                    if ret_topup["Response"]["message"] != "Success":
                        log.error('Top up failed with wrong message for card %s.' % card)
                        failed_cards[card] = 'top up failed'
                except Exception as ex:
                    log.error(str(ex))
                    failed_cards[card] = 'top up exception'
        
        # After for loop
        # print failed card summary
        if len(failed_cards) > 0:
            log.error ('Summary - Top up money failed for below cards:')
            for c,err in failed_cards:
                log.error (f'{c} : {err}')
        
        # assert fail/pass for the whole function
        assert len(failed_cards) == 0
                                       
    def test_topup_pass(self):
        log.info('Calling %s.' % inspect.stack()[0][3])

        #return if cards not defined
        try: TOPUP_PASS_CARDS
        except NameError: return
        
        # TOPUP_PASS_CARDS=['308425030450025','308425030415853']
        failed_cards = {}        
        GSTAmount = round( Topup_Pass_Zone_Amount / 11, 2)

        for card in TOPUP_PASS_CARDS:
            # get card details
            ret=self.myki_card_enquiry(card)
            if ret is None:
                log.error('myki_card_enquiry of %s failed with wrong response code.' % card)              
                failed_cards[card] = 'card enquiry failed'
            else:  
                try:
                    mykiCardStatus_ = ret["Response"]["Result"]["Card"]["mykiCardStatus"]
                    mykiCardExpiryDate_ = ret["Response"]["Result"]["Card"]["mykiCardExpiryDate"]
                    
                    orderRefNo = self.get_unique_order_no()
                    payload = {
                        "source": "PTVWebsite",
                        "Card": {
                            "mykiCardNumber": card,
                            "mykiCardStatus": mykiCardStatus_,
                            "mykiCardExpiryDate": mykiCardExpiryDate_
                        },
                        "Order": {
                            "orderReferenceNumber": orderRefNo,
                            "orderSequenceNumber": 1,
                            "amount": Topup_Pass_Zone_Amount,
                            "GSTAmount": GSTAmount,
                            "Product": {
                                "physicalZoneMin": Topup_Pass_Zone_From,
                                "physicalZoneMax": Topup_Pass_Zone_To,
                                "duration": str(Topup_Pass_Num_Days)
                            }
                        },
                        "Contact": {
                            "preferredReminder": "Email",
                            "email": Notification_Email,
                            "notification": True, # Note it is converted to json dump, it will convert to json boolean true (lower case) automatically.
                            "reminderValue": Notification_Email
                        }
                    }
                    url='https://%s/%s/ma/card/topup/mykiPass' % (api_server_url,env_id)
                    ret_topup = self.post(url, data = json.dumps(payload,indent=4))
                    # check if top up is successful
                    if ret_topup["Response"]["message"] != "Success":
                        log.error('Top up failed with wrong message for card %s.' % card)
                        failed_cards[card] = 'top up failed'
                except Exception as ex:
                    log.error(str(ex))
                    failed_cards[card] = 'top up exception'
        
        # After for loop
        # print failed card summary
        if len(failed_cards) > 0:
            log.error ('Summary - Top up ePass failed for below cards:')
            for c,err in failed_cards:
                log.error (f'{c} : {err}')
        
        # assert fail/pass for the whole function
        assert len(failed_cards) == 0                
    
    def register_myki(self, card):
        '''
        To register a myki, need below steps with the same customer information:
        - Register a AD user
        - Register customer account
        - Register myki
        - Update the AD user with customer account ID        
        '''
        log.info('Calling %s.' % inspect.stack()[0][3])
        
        # use CSN as username 
        username = card[6:-1]
        
        url='https://%s/%s/im/user/create' % (api_server_url,env_id)        
        payload = {
            "title" : "Mr",
            "firstName" : "ITF", 
            "lastName" : "NTTDATA", 
            "email" : Notification_Email,
            "username" : username,
            "password" : Account_Password,
            "customerID" : "",
            "Security" : {
                "question" : "What is your first school name?",
                "answer" : "NTTDATA"
            }
        }

        return self.post(url, data = json.dumps(payload,indent=4))
        
        
        url='https://%s/%s/im/account/registerCustomer' % (api_server_url,env_id)        
        payload = {
            "title" : "Mr",
            "firstName" : "ITF", 
            "lastName" : "NTTDATA", 
            "email" : Notification_Email,
            "username" : username,
            "password" : Account_Password,
            "customerID" : "",
            "Security" : {
                "question" : "What is your first school name?",
                "answer" : "NTTDATA"
            }
        }

        return self.post(url, data = json.dumps(payload,indent=4))
        
    def autoload_enable(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        # AUTO_LOAD_SMART_CARDS=['308425030449522']
    
    def autoload_disable(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        # AUTO_LOAD_SMART_CARDS=['308425030449522']
    
    def autoload_suspend(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        # AUTO_LOAD_SMART_CARDS=['308425030449522']
    
    def autoload_resume(self):
        log.info('Calling %s.' % inspect.stack()[0][3])
        # AUTO_LOAD_SMART_CARDS=['308425030449522']
        
    def test_autoload_smart(self):
        '''
        Smart means it follows sequence: enable -> suspend -> resume -> disable -> enable
        '''
        log.info('Calling %s.' % inspect.stack()[0][3])
        # AUTO_LOAD_SMART_CARDS=['308425030449522']
        for card in AUTO_LOAD_SMART_CARDS:
            print(card)
