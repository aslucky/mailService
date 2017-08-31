# coding: utf-8

# email server
MAIL_SERVER = 'smtp.126.com'
# MAIL_PORT = 25
MAIL_PORT = 587
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "email2918"
MAIL_PASSWORD = "1w2e3r"
MAIL_DEFAULT_SENDER =  ['xx电子发票','email2918@126.com']
MAIL_BACKEND_NOTIFY_URL_DEBUG = "http://xxx:8080/invoice-service/rest/v1/email/sendstatus/notify"
MAIL_BACKEND_NOTIFY_URL_TEST = "https://xxx:8380/invoice/v1/email/sendStatusNotify"
MAIL_BACKEND_NOTIFY_URL = "https://xxx:8380/invoice/v1/email/sendStatusNotify"
MAIL_ASCII_ATTACHMENTS = False

# administrator list
ADMINS = ['email2918@126.com','ascomtohom@126.com']
TITLE_TEMP = {
    "invoice":"您收到来自xx的电子发票"
}



