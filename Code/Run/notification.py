"""
Sends notification on sweep progress via SMTP: Argument is the message (list of pre-existing messages provided.)

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
import smtplib  
import os, sys
import numpy as np

messages = ["Successfully Received the Command", "Beginning the Parameter Sweep", "Pushing the Results","Awaiting New Command","No Tracks Found"]

fromaddr = ''  
toaddrs  = ''  
if 'm' in sys.argv[2]:
	msg = sys.argv[1] + "   " + sys.argv[3]
else:	
	msg = sys.argv[1] + "   " + messages[int(sys.argv[2])]

# Credentials (if needed)  
username = ''  
password = ''  
  
# The actual mail send  
server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(username,password)  
server.sendmail(fromaddr, toaddrs, msg)  
server.quit()  
