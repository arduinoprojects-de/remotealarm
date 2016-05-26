import config_sendsms
import requests

class SMS:
    def __init__(self):
        self.apiUrl = config_sendsms.api['url']
        self.apiGateway = config_sendsms.api['gateway']
        self.apiUser = config_sendsms.api['user']
        self.apiPassword = config_sendsms.api['password']
        
    def setMessage(self, message):
        self.message = message
        
    def send(self):
        for receiver in config_sendsms.alarm:
            r = requests.get("{}?id={}&pw={}&type={}&empfaenger={}&text={}" . format(self.apiUrl, self.apiUser, self.apiPassword, self.apiGateway, receiver, self.message))
            print(r.text)
        

