''' 
*** Test card data ***
Examples:
['308425030410763','308425030415820']   - Multiple cards
['308425030410763']                     - one card
[]                                      - Don't execute
# TOPUP_MONEY_CARDS=['308425030416901'] - Don't execute
'''
TOPUP_MONEY_CARDS=['308425030416901'] # ['308425030416901','308425030415820']
TOPUP_PASS_CARDS= ['308425030450025'] # ['308425030450025','308425030449522']

# Smart means it follows sequence: enable -> suspend -> resume -> disable -> enable
AUTO_LOAD_SMART_CARDS=[] # '308425030449522'
#CARD_ENQUIRY_CARDS=['308425030416901']

# *** API automation parameters ***
env_id='sit'
api_server_url=r'SITLNXAPIGWAY1.SITPROD1ENV.LOCAL:7443'
ClientID='l7b399dd15b5d5410e94d8081bb022dd31'
ClientSecret='ad03cddf18304d528013ae29bdcb4b75'
creditCard_token = '0157205482641111'
creditCardExpiryDate = r'08/2020'

# Test data parameters
Notification_Email='peter.xie@nttdata.com'
Topup_Money_Amount=20
Topup_Pass_Num_Days=7
Topup_Pass_Zone_From=1
Topup_Pass_Zone_To=2
Topup_Pass_Zone_Amount=44.00
Auto_Load_Threshold=10
Auto_Load_Amount=10
Account_Password='keane*12'