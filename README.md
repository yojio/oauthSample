### OAuth sample application

for facebook,twitter,linkedin and google+

This works on the google app engine(python -2.7).  
You will need to edit the config.py to suit your own environment . 

callback-url:  
  self.request.host_url + "/callback/twitter" # twitter oauth1.0a  
  self.request.host_url + "/callback/twitterapp" # twitter oauth2.0  
  self.request.host_url + "/callback/google" # google  
  self.request.host_url + "/callback/facebook" # facebook  
  self.request.host_url + "/callback/linkedin" # linkedin

Required Library  
Google+ API Client Library for Python  
Google OAuth2 API Client Library for Python  

apiclient  
httplib2  
oauth2  
oauth2client  
uritemplate  
gflags  
