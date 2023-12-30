# ------------------------------------------------------------
#   Developer    : Aman Ranjan (aman.ranjan@mapmyindia.com)  |
#   Project Name : NDS-LOGIN-PORTAL                          |
#   Copyright    :                                           |
#   Year         : 2023                                      |
# ------------------------------------------------------------

import configparser, os

configs = configparser.ConfigParser()
configs.read(os.path.join('config', 'config.ini'))
dbConfigs = configs['postgresql']
pathConfig = configs['paths']
logConfig = configs['loggings']
mongoConfig = configs['mongo-db']
activeDbConfig = configs['active-db']
companyConfig = configs['company']

credentialsCollection = configs['mongo-credentials-collection']
credentialsSchema =  configs['postgresql-credentials-schema']


location = pathConfig['location']
