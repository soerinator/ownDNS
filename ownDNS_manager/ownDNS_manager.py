#!/usr/bin/env python

"""ownDNS manager class

This class is the ownDNS manager, which uploades an html page that includes your home IP to a Dropbox directory
if the IP gets changed so that you can ever reach your home server without having a registered domain or dynDNS service 
running. 


Requirements:
	Follwoing is required to get the ownDNS functional:
		1) a Dropbox account
		2) The Dropbox-Uploader, which is available at GitHub: https://github.com/andreafabrizi/Dropbox-Uploader
		3) A configured system mail transfer agent (MTA) like postfix, if mail notification feature shall be used
		4) All python modules which gets imported at this program file 

Install/Use:

	1) get the software
		1.1) clone ownDNS_manager by: "git clone https://github.com/soerinator/ownDNS_manager.git"
		1.2) enter the dirctory "ownDNS" and clone the Dropbox-Uploader by "git clone https://github.com/andreafabrizi/Dropbox-Uploader.git"
	   
	   -> directory structure should look like:
	       - ownDNS
	         -ownDNS_manager
		 -Dropbox-Uploader
	
	2) Configure the software
		2.1) now configure Dropbox-Uploader as described on Dropbox-Uploader manual (Readme)
		2.2) open ownDNS_manager.py and configure by setting all DEF_* gloabal variables (DEF_MAIL_ENABLED, ...)
		2.3) add ownDNS_manager.py file to cron-jobs to be runned periodically
	     		- enter command "crontab -e"
	     		- add following line to crontab
	            		*/30 *  * * *   /usr/bin/python [path-to-programm]/ownDNS_manager.py >/dev/null 2>&1
			- save and close crontab
		  		-> ownDNS_manager is started avery 30 minutes now
		 
		2.4) make ownDNS_manager.py executable by enering follwing command
			chmos +x ownDNS_manager.py
	3) start test by entering test commands which can be found by entering following on CLI
		./ownDNS_manager.py --help

Hint:
	Ensure that only you (the Dropbox-uploader) can write to your Dropbox folde on which the html file with your IP 
	will be stored!

Version:
 
	$Date: 2017-06-19 22:38:25 +0200 (Mon, 19 Jun 2017) $
 
	$Rev: 340 $

"""


import argparse

import time
import datetime

import urllib2
from subprocess import PIPE, Popen

import os
import socket


class ownDNS_manager:


	#MAIL - can be used to get notifications per mail in case 
	#	* IP changed
	DEF_MAIL_ENABLED		= False					#set True to enable mail, Flase to disable mail
	DEF_MAIL_RECEIVER		= "yourmailaddress@gmx.de"		#mail receiver (to) address
										#for multi receiver addresses: "mail1@gmx.de, mail2.gmx.de"
	
	#LOG FILES
	DEF_IP_CHANGE_LOG_FILE		= '/ownDNS/ip_change.log'		#location and name of IP change log file
	DEF_UPLOAD_LOG_FILE		= '/ownDNS/dropbox_upload.log'		#location and name of upload log file

	#IP STORAGE
	DEF_LAST_IP			= '/ownDNS/last_ip.txt'			#last used ip 

	#HTML WITH IP TO BE UPLOADED
	DEF_UPLOAD_HTML			= '/ownDNS/find_home.html'		#HTML whihc has to be uploaded (inclusive complete path)
	
	#DROPBOX UPLOAD PARAMETERS
	DEF_DBOX_CMD			= 'upload'				#command for upload (download is also possible, but not used here)
	DEF_DBOX_FOLDER			= 'Public'				#folder on which the file will be uploaded
	DEF_DBOX_UPLOADER		= '/ownDNS/Dropbox-Uploader/dropbox_uploader.sh'		#upload script				
	
	DEF_DBOX_HTML_LNK		= 'https://www.dropbox.com/[your_directory]/find_home.html?dl=1&pv=1'	#link to uploaded html which includes the ip

	

	def send_mail_ip_changed(self,old_ip,new_ip,debug):
		"""sent mail to inform abaout IP change by using system MTA (e.g. postfix)

		Args:
			ild_ip: old ip
			new_ip: new ip
			debug: enable additional debug info

		Returns:
			nothing

		ToDo:
			nothing		
		
		"""

		if(debug):
			print("Sending mail to: "+self.DEF_MAIL_RECEIVER)


		msg = "Hi,\n\n    the IP has been changed from: "+old_ip+" to: "+new_ip+".\n\nBest regards,\nYour loving Home"
		subject = "ownDNS: INFO"
		
		self.send_mail(msg,subject,debug)


	def send_mail_ip_check_error(self,old_ip,debug):
		"""sent mail to inform about ip check error by using system MTA (e.g. postfix)

		Args:
			debug: enable additional debug info

		Returns:
			nothing

		ToDo:
			nothing		
		
		"""

		if(debug):
			print("Sending mail to: "+self.DEF_MAIL_RECEIVER)


		msg = "Hi,\n\n    there was an error during external check of current own ip. Current IP "+old_ip+" has not been changed.\n\nBest regards,\nYour loving Home"
		subject = "ownDNS: ERROR"
		
		self.send_mail(msg,subject,debug)
		
		
	def send_mail_upload_error(self,old_ip,debug):
		"""sent mail to inform about upload error by using system MTA (e.g. postfix)

		Args:
			debug: enable additional debug info

		Returns:
			nothing

		ToDo:
			nothing		
		
		"""

		if(debug):
			print("Sending mail to: "+self.DEF_MAIL_RECEIVER)


		msg = "Hi,\n\n    there was an error during upload of HTML with new IP. \n\nBest regards,\nYour loving Home"
		subject = "ownDNS: ERROR"
		
		self.send_mail(msg,subject,debug)
		
		
	def send_mail(self,msg,subject,debug):
		"""send mail per system MTA as sub-process

		Args:
			msg: mail message
			subject: mail subject
			debug: enable additional debug info

		Returns:
			nothing

		ToDo:
			nothing		
		
		"""
		 
		#send mail by subprocess
		p1 = Popen(["echo",msg], stdout=PIPE)
		p2 = Popen(["mail","-s",subject,self.DEF_MAIL_RECEIVER], stdin=p1.stdout,stdout=PIPE)
		
		ret_value = p2.communicate()[0]

		if(debug):
			print("Mail process started with return value: "+ret_value)
		
	
	def get_timestamp(self):
		"""get actual time

		Args:
			none 

		Returns:
			time stamp

		ToDo:
			nothing		
		"""
		ts_n = time.time()
		ts = datetime.datetime.fromtimestamp(ts_n).strftime('%Y-%m-%d %H:%M:%S')	
		return ts 
	
	
	def log_ip_change(self,last_ip, act_ip):
		"""log IP change (write it to log file)

		Args:
			last_ip	:	last IP 
			act_ip	:	actual IP  		
		
		Returns:
			none
		
		ToDo:
			nothing
		"""
		
		log_line = "ip changed from: "+last_ip+" to: "+act_ip+ " at: " +  self.get_timestamp() + "\n"
		text_file = open(self.DEF_IP_CHANGE_LOG_FILE, "a")
		text_file.write(log_line);
		text_file.close()


	def log_ip_check(self):
		"""log check of IP

		Args:
			none
					
		Returns:
			none
		
		ToDo:
			nothing
		"""

		log_line = "ip check done at: " +  self.get_timestamp() + "\n"
		text_file = open(self.DEF_IP_CHANGE_LOG_FILE, "a")
		text_file.write(log_line);
		text_file.close()


	def dropbox_html_upload(self,debug):
		"""upload html to Dropbox

		Args:
			debug: enable additional debug info
					
		Returns:
			none
		
		ToDo:
			nothing
		"""
	
		if(debug):
			print("\n     -> upload html file to Dropbox")


		#log upload
		upload_log_file = open(self.DEF_UPLOAD_LOG_FILE, "a")

		#check if iploader is available
		if(os.path.isfile(self.DEF_DBOX_UPLOADER)):	
	
			#Dropbox uploader
			ret_value = Popen([self.DEF_DBOX_UPLOADER, self.DEF_DBOX_CMD, self.DEF_UPLOAD_HTML, self.DEF_DBOX_FOLDER], stdout=PIPE).communicate()[0]
				
			log_line = "start upload of new html at: "+ self.get_timestamp()+"\n    ";

			if(debug):
				print(log_line)
				print("Process return-value: \n"+ret_value +"\n")

		else:
			log_line = "ERROR: Dropbox-Uploader not available!"
			ret_value = ""
			print(log_line)


		upload_log_file.write(log_line);
		upload_log_file.write(ret_value);
		upload_log_file.close()



	def write_html(self,ip,debug):
		"""write html with new IP included

		Args:
			ip: the new ip which wil be embedded in the html file
			debug: enable additional debug info
					
		Returns:
			none
		
		ToDo:
			nothing
		"""

		if(debug):
			print("\n     -> write html file with IP :"+ip)


		text_file = open(self.DEF_UPLOAD_HTML, "w")
		text_file.write("<html>\n");
		text_file.write("<head><title>Find Home Web-Server </title>\n");
		text_file.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, user-scalable=yes\">");
		text_file.write("<meta http-equiv=\"refresh\" content=\"2; URL=https://"+ip+"\">");
		text_file.write("</head>\n");
		text_file.write("<body>\n");
		text_file.write("<h1>way to home</h1>\n");
		text_file.write("<meta name=\"ip_to_home\" content=\""+ip+"\">");
		text_file.write("<p><a href=\"https://"+ip+"\">GO HOME</a></p>\n");
		text_file.write("</body>\n");
		text_file.write("</html>\n");
		text_file.close()
		return 
		

	def check_dropbox_html(self):
		"""downloads the uploaded html and prints it on CLI

		Args:
			none
					
		Returns:
			none
		
		ToDo:
			nothing
		"""

		#get dropbox html

		try:	
			response = urllib2.urlopen(self.DEF_DBOX_HTML_LNK)
			html = response.read()	
			print html
		except urllib2.HTTPError as e:
			error_message = e.read()
			print error_message


	def get_old_ip(self,debug):
		"""get old/last used ip from file

		Args:
			debug: enable additional debug info
					
		Returns:
			old ip (last used/saved ip)
		
		ToDo:
			nothing
		"""
				
		if(os.path.isfile(self.DEF_LAST_IP)):
			f = open(self.DEF_LAST_IP)
			lines = f.readlines()
			if len(lines) > 0:
				old_ip = lines[0];
			else:
				old_ip = "0.0.0.0"

			f.close()
		else:
			#create ip log file and save initial IP 
			old_ip = "0.0.0.0"
			self.save_new_ip(old_ip,debug)
			
			if(debug):
				print("\nWARNING: "+self.DEF_LAST_IP+" does not exist!")
				print("\n     -> generate it with initial IP :"+old_ip)

		#clean it up
		old_ip = old_ip.strip()

		return old_ip


	
	def save_new_ip(self,ip,debug):		
		"""save actual ip to have it later for checks if there was a change

		Args:
			ip: ip to be saved
			debug: enable additional debug info
					
		Returns:
			none
					
		ToDo:
			nothing
		"""
		
		if(debug):
			print("\n     -> log IP :"+ip)
		
		text_file = open(self.DEF_LAST_IP, "w")
		text_file.write(ip)
		text_file.close()
		
	
	
	def check_ip(self,ip):
		"""check if we have an IP or not

		Args:
			ip: ip
					
		Returns:
			true in case it is an IP or false in case it is no valid IP 
		
		ToDo:
			nothing
		
		"""
	
		try:
			socket.inet_aton(ip)
			return True
		except:
			return False
	
		
	def get_actual_ip(self,service):
		"""get actual ip by external service

		Args:
			service: curl or dig
					
		Returns:
			actual ip 
		
		ToDo:
			nothing
		"""
		
		
		if(service=="dig"):
			act_ip = Popen(["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"], stdout=PIPE).communicate()[0]
		
		else:
			act_ip = Popen(["curl", "ifconfig.co"], stdout=PIPE).communicate()[0]
			#act_ip = Popen(["curl", "curlmyip.com"], stdout=PIPE).communicate()[0]
		
		#clean up the result
		act_ip  = act_ip.replace('\n', '').replace('\r', '')

		
		#check ip
		chkip_res = self.check_ip(act_ip)
		
		#do another try if it failed
		if(chkip_res):
			if(service=="dig"):
				act_ip = Popen(["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"], stdout=PIPE).communicate()[0]
			else:
					act_ip = Popen(["curl", "ifconfig.co"], stdout=PIPE).communicate()[0]
		
			#clean up the result
			act_ip  = act_ip.replace('\n', '').replace('\r', '')
		
		return act_ip
		

	def upload_error_chk(self):
		"""check upload logfile for upload errors

		Args:
			none
					
		Returns:
			1 - in case of error, 0 - in case of no error 
		
		ToDo:
			nothing
		"""
	
		search_str = "Error"	#searchstring for error
		last_line = ""
	 	
		#check if file exist
		if(os.path.isfile(self.DEF_UPLOAD_LOG_FILE)):
			a=1
		else:
			f = open(self.DEF_UPLOAD_LOG_FILE, "w")	#create file if not exist to avaoid error on next steps 	
	
	
		#re-open and read from it
		f = open(self.DEF_UPLOAD_LOG_FILE)
		lines = f.readlines()
		f.close()
	
		if lines:
        		first_line = lines[:1]
        		last_line = lines[-1]
		
		if search_str in last_line : #check for error on last entry/line
			#print("Error on last upload!");
			return 1
		else:
			#print("All OK on last upload!");
			return 0
		
		
	def owndns_manager(self,debug,test_forceIPchange,test_forceUpload):
		"""manager for ownDNS service

		Args:
			none
					
		Returns:
			none 
		
		ToDo:
			nothing
		"""
		
		#get current IP
		act_ip = self.get_actual_ip("curl")
		#get saved IP
		old_ip = self.get_old_ip(debug)


		#check current IP
		act_ip_is_ip = self.check_ip(act_ip)
		
		
		if(debug):
			print("\nactual IP is:"+act_ip)
			print("lastIP was  :"+old_ip+"\n")
		
		#fore IP change as test
		if(test_forceIPchange):
			if(old_ip == "99.99.99.99"):
				act_ip = "0.0.0.0"		
			else:
				act_ip = "99.99.99.99"		
			
			print("\n    -> Force IP change to: "+act_ip+"\n")
			


		#fore IP change as test
		if(test_forceUpload):
			print("\n   -> Force Upload\n")		


		if ((old_ip == act_ip) | (act_ip=="")) & (not test_forceUpload):
			if(debug):
				print "     -> no IP change!\n"
			        print self.get_timestamp()
			
			#do nothing
			a=1
		else:

			if(act_ip_is_ip):

				if(debug):
					print "     -> IP is OK and has been changed!\n"
			        	print self.get_timestamp()
			
			
				#manage IP change 
			
				#send mailinfo
				if(self.DEF_MAIL_ENABLED==True):
					self.send_mail_ip_changed(old_ip,act_ip,debug)
				
				#upload new IP
				self.save_new_ip(act_ip,debug)
				self.write_html(act_ip,debug)
				self.dropbox_html_upload(debug)	
				self.log_ip_change(old_ip, act_ip)
				a=2
			else:
				#IP is incorrect			
				if(debug):
					print "IP "++" is NOT OK! No action done!\n"


				#send mailinfo
				if(self.DEF_MAIL_ENABLED==True):
					self.send_mail_ip_check_error(old_ip,debug)

			
		
		#check if upload was error-free
		#if not, upload again
		if self.upload_error_chk() == 1:
			if(debug):
				print("\nERROR on uploadd etected ... try to upload again ..... \n")
				
			#send mailinfo
			if(self.DEF_MAIL_ENABLED==True):
				self.send_mail_upload_error(old_ip,debug)
			
		
	
if __name__ == "__main__":
	"""Main 
	
	
	"""
		
	parser = argparse.ArgumentParser(description="ownDNS manager to organise own dynamical IP update on www.")
	parser.add_argument("--test_getIP","-tgip", help="get and show actual IP on CLI as test",action='store_true') 
	parser.add_argument("--test_getHTML","-tghtml", help="get and show uploaded HTML on CLI as test",action='store_true') 
	parser.add_argument("--test_getActualLoggedIP","-tgalip", help="show last logged IP",action='store_true') 
	parser.add_argument("--test_getTimeStamp","-tgts", help="get and show time stamp",action='store_true') 
	parser.add_argument("--test_forceIPchange","-tfipc", help="force ip change as test to check manager and upload",action='store_true') 
	parser.add_argument("--test_forceUpload","-tfup", help="force html upload",action='store_true') 
	parser.add_argument("--debug","-d", help="show additional debug messages",action='store_true') 
	parser.add_argument("--chekip","-chkip", help="check given IP (e.g.: -chkip 129.23.212.23)") 
	parser.add_argument("--test_sendIPChangeInfo","-tsipci", help="send test mail about ip change",action='store_true') 
		
		
	args = parser.parse_args()

	odnsm = ownDNS_manager()	#generate instance

	if(args.test_getIP):
		#get ip per service and show on CLI
		act_ip = odnsm.get_actual_ip("curl")
		print("\nActual IP is: "+act_ip+"\n")


	elif(args.test_getHTML):
		#check if uploaded html contains ip
		print("\nHTML on Dropbox is:\n");
		odnsm.check_dropbox_html()
		print("\n")

	elif(args.test_getActualLoggedIP):
		#show last loged IP
		act_logged_ip = odnsm.get_old_ip(args.debug)
		print("\nActual logged IP is: "+act_logged_ip+"\n")
		
	elif(args.test_getTimeStamp):
		#show last loged IP
		ts = odnsm.get_timestamp()
		print("\nTimeStamp is: "+ts+"\n")


	elif(args.chekip):
		#check ip
		res = odnsm.check_ip(args.chekip)
		
		if(res):			
			print("\nIP: "+args.chekip+" -> is OK!\n")
		else:
			print("\nIP: "+args.chekip+" -> is NOT OK!\n")
					#get saved IP
			old_ip = odnsm.get_old_ip(args.debug)
			odnsm.send_mail_ip_check_error(old_ip,args.debug)		


	elif(args.test_sendIPChangeInfo):
		odnsm.send_mail_ip_changed("99.99.99.99","0.0.0.0",args.debug)

	else:
		#manage IP change
		odnsm.owndns_manager(args.debug,args.test_forceIPchange,args.test_forceUpload)
		
