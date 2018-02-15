# ownDNS
A private alternative solution to usually used DNS services like DynDNS.

ownDNS shall be a private service which enables you to find your own server without registering a domain. It uploads the own IP, wrapped in an html page, to a 24/7 accessible cloud storage like Dropbox. This enables you to find your home server at any time, also if the IP has been changed. It is like an (dyn)DNS service, but with own and free available recources. 

## Requirements

Follwoing is required to get the ownDNS functional:
1) a Dropbox account
2) The Dropbox-Uploader, which is available at GitHub: https://github.com/andreafabrizi/Dropbox-Uploader
3) A configured system mail transfer agent (MTA) like postfix, if mail notification feature shall be used
4) All python modules which gets imported at this program file 

## Install/Use

1) get the software
   
   1.1) clone ownDNS_manager by: "git clone https://github.com/soerinator/ownDNS_manager.git"
   
   1.2) enter the dirctory "ownDNS" and clone the Dropbox-Uploader by "git clone https://github.com/andreafabrizi/Dropbox-Uploader.git"
	   
	        -> directory structure should look like:
	           - ownDNS
	              -ownDNS_manager
                 ownDNS_manager.py
		             -Dropbox-Uploader
                 ...
	
2. Configure the software

   2.1. now configure Dropbox-Uploader as described on Dropbox-Uploader manual (Readme)

   2.2. open ownDNS_manager.py and configure by setting all DEF_* gloabal variables (DEF_MAIL_ENABLED, ...)

   2.3. add ownDNS_manager.py file to cron-jobs to be runned periodically

        - enter command "crontab -e"

        - add following line to crontab
             */30 *  * * *   /usr/bin/python [path-to-programm]/ownDNS_manager.py >/dev/null 2>&1

       - save and close crontab
        
		  		     -> ownDNS_manager is started avery 30 minutes now
		 
   2.4. make ownDNS_manager.py executable by enering follwing command
			       
          chmos +x ownDNS_manager.py

3. start test by entering test commands which can be found by entering following on CLI
		        
          ./ownDNS_manager.py --help

## Hint
Ensure that only you (the Dropbox-uploader) can write to your Dropbox folder on which the html file with your IP will be stored! 
