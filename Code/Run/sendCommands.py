"""
Uses SMTP to send commands to the listening address on alternate computers

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
import smtplib  
import os, sys
import numpy as np

comps = sys.argv[1][1:-1].split(",")
sweep = sys.argv[2]

fromaddr = ''  
toaddrs  = '' 

# Credentials (if needed)  
username = ''  
password = ''  
  
# The actual mail send  
server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(username,password)  
for comp in comps:
	msg = "Subject:CommenceSweep:Comp%s-%s\n\n" % (comp,sweep)
	server.sendmail(fromaddr, toaddrs, msg)  
server.quit()  

