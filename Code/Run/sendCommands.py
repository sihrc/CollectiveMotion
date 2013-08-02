""" Uses SMTP to send commands to the listening address on alternate computers """
import smtplib  
import os, sys
import numpy as np

comps = sys.argv[1][1:-1].split(",")
sweep = sys.argv[2]

fromaddr = 'christopher.lee.olin@gmail.com'  
toaddrs  = 'c.sihrc.lee@gmail.com' 

# Credentials (if needed)  
username = 'christopher.lee.olin'  
password = 'Cl120193'  
  
# The actual mail send  
server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(username,password)  
for comp in comps:
	msg = "Subject:CommenceSweep:Comp%s-%s\n\n" % (comp,sweep)
	server.sendmail(fromaddr, toaddrs, msg)  
server.quit()  

