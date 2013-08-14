"""
Runs on alternate computers with argument [1,2,3,4,5] for respective decreasing densities ([High, TwoThirds, ...]).
Listens for command issued to specified email address. Turns on and off with ready.txt located on the server. Without
the on and off feature, gmail (any server) will deny access with too many repeated log ins.

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
import poplib, sys, time
from subprocess import call
from email import parser

def checkEmail():
	""" 
	Checks email for command
	"""
	pop_conn = poplib.POP3_SSL('pop.gmail.com')
	pop_conn.user('')
	pop_conn.pass_('')
	#Get messages from server:
	messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
	# Concat message pieces:
	messages = ["\n".join(mssg[1]) for mssg in messages]
	#Parse message intom an email object:
	messages = [parser.Parser().parsestr(mssg) for mssg in messages]
	flag = 0
	sweep = None
	for message in messages:
		subject = message['subject']
		if subject is None:
			continue
		elif "CommenceSweep:" in subject:
			start = subject.find(":")
			command = subject[start+1:]
			print command
			if "Comp"+sys.argv[1] in command:
				start = command.find("-")
				sweep = command[start+1:]
				print sweep
				poplist = pop_conn.list()
				msglist = poplist[1]
				for msgspec in msglist:
					delete = int(msgspec.split(' ')[0])
					pop_conn.dele(delete)
				flag = 1
	pop_conn.quit()
	return flag, sweep

def checkMode():
	with open("Z:\\2013 Summer\\ready.txt", "rb") as f:
			currentline = None
			while currentline != "":
				currentline = f.readline()
				if "Comp" + sys.argv[1] in currentline:
					start = currentline.find(":")
					return currentline[start+1:]

if __name__ == "__main__":
	i = 0
	while (1):
		if "on" in checkMode():
			if i == 1:
				print "Standing By: Waiting for Command"
				flag, sweep = checkEmail()
				if flag:
					call(["python", "automatedRun.py", sweep, sys.argv[1]])
		else:
			if i == 1:
				print "Off Mode: Not receiving commands."
		i = i%500 + 1