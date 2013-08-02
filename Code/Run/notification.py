"""
Sends notification on sweep progress via SMTP: Argument is the message (list of pre-existing messages provided.)
"""
import smtplib  
import os, sys
import numpy as np

messages = ["Successfully Received the Command", "Beginning the Parameter Sweep", "Pushing the Results","Awaiting New Command","No Tracks Found","Something failed in the run"]

fromaddr = 'c.sihrc.lee@gmail.com'  
toaddrs  = 'sihrc.c.lee@gmail.com'  
msg = sys.argv[1] + "   " + messages[int(sys.argv[2])]

# Credentials (if needed)  
username = 'c.sihrc.lee'  
password = 'Cl120193'  
  
# The actual mail send  
server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(username,password)  
server.sendmail(fromaddr, toaddrs, msg)  
server.quit()  
