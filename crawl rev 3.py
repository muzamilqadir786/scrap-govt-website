
#===========================#
# Instructions: 
# INSTALL MODULES (requests,beautifulsoup4,lxml)
# INSTALL mysqldb package from http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python and install it if on Windows
# Set the Settings of Mysql
#===========================

import re
import urllib2
import csv
import requests
#import bs4
from bs4 import BeautifulSoup
import lxml.html
from lxml import etree

from dateutil.parser import parse

"""Handling unicode characters """
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


# Setting up database Connection Variables
import MySQLdb

# Host =  "184.154.229.16"
# Username =  "photonen_fboadm"
# Password =  "MCMmL[p};f#m"
# Database =  "photonen_fbo"
# Table = "fbo"
# Port =  "3306"

Host =  "localhost"
Username =  "root"
Password =  ""
Database =  "photonen_fbo"
Table = "fbo"
Port =  "3306"


base_url = "https://www.fbo.gov"

def contracting_office_info(html):
	#Getting Fields from 10 to 14
	contracting_office_info = html.xpath('//div[@id="dnf_class_values_procurement_notice__office_address__widget"]/text()')                    
	contracting_office_info = [re.sub('[\s]',' ',info).strip() for info in contracting_office_info]
	
	ctr_office_street = ctr_office_city = ctr_office_state = ctr_office_zip = ctr_office_country = None
	if contracting_office_info:
		# Field 10
		ctr_office_street = contracting_office_info[0]
		ctr_office_city_state_zip = contracting_office_info[1]
		
		if ctr_office_city_state_zip:
			ctr_office_city_state_zip = contracting_office_info[1].split(',')
			 # Field 11
			try:
				ctr_office_city = ctr_office_city_state_zip[0]
				ctr_office_state_zip = ctr_office_city_state_zip[1].split()
				# Field 12
				ctr_office_state = ctr_office_state_zip[0]
				# Field 13
				ctr_office_zip = ctr_office_state_zip[1]    
			except IndexError:
				print "Error importing solicitation.  Skipping record." 
				# sys.exit(1)
			
		#Field 14 
		try:
			ctr_office_country = contracting_office_info[2]
		except:
			print "Country not exists"

	return [ctr_office_street,ctr_office_city,ctr_office_state,ctr_office_zip,ctr_office_country]

	# return [re.sub('[\s]',' ',str(sa)).strip() for sa in s] 
									
def primary_point_of_contact(html):
	ppc_first_name = ppc_last_name = ppc_title = ppc_email = ppc_phone = ppc_fax = None
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[1]/text()'):
		ppc_name = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[1]/text()')
		if ppc_name:
			name = ppc_name[0].split()
			ppc_first_name = name[0]
			ppc_last_name = name[1]        
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[2]/text()'):
		ppc_title = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[2]/text()')[0]
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[3]/a/text()'):
		ppc_email = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[3]/a/text()')[0]
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[4]/text()'):
		ppc_phone = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[4]/text()')[0]
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[5]/text()'):
		ppc_fax = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[5]/text()')[0]

	s = [ppc_first_name,ppc_last_name,ppc_title,ppc_email,ppc_phone,ppc_fax]
	
	return [re.sub('[\s]',' ',str(sa)).strip() for sa in s] 

def secondary_point_of_contact(html):
	
	spc_first_name=spc_last_name=spc_title=spc_email=spc_phone=spc_fax=None
	if html.xpath('//div[@id="so_formfield_dnf_class_values_procurement_notice__secondary_poc_"]'):
		if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[1]/text()'):
			spc_name = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[1]/text()')
			name = spc_name[0].split()
			spc_first_name = name[0]
			spc_last_name = name[1] 
		if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[2]/text()'):    
			spc_title = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[2]/text()')[0]
		if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[3]/a/text()'):
			spc_email = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[3]/a/text()')[0]
		if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[4]/text()'):
			spc_phone = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[4]/text()')[0]
		if html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[5]/text()'):
			spc_fax = html.xpath('//div[@id="dnf_class_values_procurement_notice__primary_poc__widget"]/div[5]/text()')[0]

		s = [spc_first_name,spc_last_name,spc_title,spc_email,spc_phone,spc_fax]
		return [re.sub('[\s]',' ',str(sa)).strip() for sa in s]


def general_information(html):

	original_posted_date=posted_date=response_date=original_response_date=archive_policy=original_archive_date=archive_date=original_set_aside=set_aside=None
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__original_posted_date__widget"]/text()'):
		original_posted_date = html.xpath('//div[@id="dnf_class_values_procurement_notice__original_posted_date__widget"]/text()')[0]
		# print original_posted_date
		original_posted_date  = re.sub('[\s]',' ',str(original_posted_date)).strip()
		if original_posted_date in [None,"-","None"]:
			original_posted_date = None 
		else:
			original_posted_date_match = re.match('\w*\s\d\d\,\s\d{4}',original_posted_date)
			if original_posted_date_match:
				# print original_posted_date_match.group()
				original_posted_date = str(parse(original_posted_date_match.group())).split()[0]

	if html.xpath('//div[@id="dnf_class_values_procurement_notice__posted_date__widget"]/text()'):
		posted_date = html.xpath('//div[@id="dnf_class_values_procurement_notice__posted_date__widget"]/text()')[0]
		posted_date  = re.sub('[\s]',' ',str(original_posted_date)).strip()        
		if posted_date in [None,"-","None"]:
			posted_date = None 
		else:
			posted_date_match = re.match('\w*\s\d\d\,\s\d{4}',posted_date)
			if posted_date_match:
				# print posted_date_match.group()
				posted_date = str(parse(posted_date_match.group())).split()[0]

	if html.xpath('//div[@id="dnf_class_values_procurement_notice__response_deadline__widget"]/text()'):
		response_date = html.xpath('//div[@id="dnf_class_values_procurement_notice__response_deadline__widget"]/text()')[0]
		response_date  = re.sub('[\s]',' ',str(response_date)).strip()        
		if response_date in [None,"-","None"]:
			response_date = None 
		else:
			response_date_match = re.match('\w*\s\d\d\,\s\d{4}',response_date)
			if response_date_match:
				# print response_date_match.group()
				response_date = str(parse(response_date_match.group())).split()[0]

	if html.xpath('//div[@id="dnf_class_values_procurement_notice__original_response_deadline__widget"]/text()'):
		original_response_date = html.xpath('//div[@id="dnf_class_values_procurement_notice__original_response_deadline__widget"]/text()')[0]
		original_response_date  = re.sub('[\s]',' ',str(original_response_date)).strip()
		# print original_response_date
		if original_response_date in [None,"-","None"]:
			original_response_date = None 
		else:
			original_response_date_match = re.match('\w*\s\d\d\,\s\d{4}',original_response_date)
			if original_response_date_match:
				# print original_response_date_match.group()
				original_response_date = str(parse(original_response_date_match.group())).split()[0]

	if html.xpath('//div[@id="dnf_class_values_procurement_notice__archive_type__widget"]/text()'):
		archive_policy = html.xpath('//div[@id="dnf_class_values_procurement_notice__archive_type__widget"]/text()')[0]

	if html.xpath('//div[@id="dnf_class_values_procurement_notice__original_archive_date__widget"]/text()'):
		original_archive_date = html.xpath('//div[@id="dnf_class_values_procurement_notice__original_archive_date__widget"]/text()')[0]
		original_archive_date  = re.sub('[\s]',' ',str(original_archive_date)).strip()
		# print original_archive_date
		if original_archive_date in [None,"-","None"]:
			original_archive_date = None 
		else:
			original_archive_date_match = re.match('\w*\s\d\d\,\s\d{4}',original_archive_date)
			if original_archive_date_match:
				# print original_archive_date_match.group()
				original_archive_date = str(parse(original_archive_date_match.group())).split()[0]

	if html.xpath('//div[@id="dnf_class_values_procurement_notice__archive_date__widget"]/text()'):
		archive_date = html.xpath('//div[@id="dnf_class_values_procurement_notice__archive_date__widget"]/text()')[0]
		archive_date  = re.sub('[\s]',' ',str(archive_date)).strip()
		print archive_date
		if archive_date in [None,"-","None"]:
			archive_date = None
		else:
			archive_date_match = re.match('\w*\s\d\d\,\s\d{4}',archive_date)
			if archive_date_match:
				# print archive_date_match.group()
				archive_date = str(parse(archive_date_match.group())).split()[0]
						
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__original_set_aside__widget"]/text()'):
		original_set_aside = html.xpath('//div[@id="dnf_class_values_procurement_notice__original_set_aside__widget"]/text()')[0]
	if html.xpath('//div[@id="dnf_class_values_procurement_notice__set_aside__widget"]/text()'):
		set_aside = html.xpath('//div[@id="dnf_class_values_procurement_notice__set_aside__widget"]/text()')[0]  


	s = [original_posted_date,posted_date,response_date,original_response_date,archive_policy,original_archive_date,archive_date,original_set_aside,set_aside]   

	return [re.sub('[\s]',' ',str(sa)).strip() for sa in s]  

def btn_links(html):
	watch_opportunity_link = html.xpath('//div[contains(@class,"buttonbar_top ")]/input[2]/@onclick')
	interested_vendors_link = html.xpath('//div[contains(@class,"buttonbar_top ")]/input[3]/@onclick')
	packages_link = html.xpath('//a[contains(text(),"Packages")]/@href')
	interested_vendors_tab = html.xpath('//a[contains(text(),"Packages")]/@href')
	print packages_link
	# sys.exit(1)
	if watch_opportunity_link:
		watch_opportunity_link = re.search("'[\w\W]*'",str(watch_opportunity_link[0])).group().strip("'")
		watch_opportunity_link = base_url+watch_opportunity_link
	if interested_vendors_link:
		interested_vendors_link = re.search("'[\w\W]*'",str(interested_vendors_link[0])).group().strip("'")
		interested_vendors_link = base_url+interested_vendors_link
	else:
		interested_vendors_link = ' ' 
	if packages_link:
		packages_link = base_url+packages_link[0]
	if interested_vendors_tab:
		interested_vendors_tab = base_url+interested_vendors_tab[0]

	return [watch_opportunity_link,interested_vendors_link,packages_link,interested_vendors_tab]

	
	# if html.xpath('//div[contains(@class,"buttonbar_top ")]/input[2]/@onclick'):

### Modified extract to take keywords and naics code as arguments.
def extract(url,search_keywords,search_naics_code):
	detail_urls = []
	headers = {     
		"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	}

	data= {
		'_____dummy':'dnf_',
		'so_form_prefix':'dnf_',
		'dnf_opt_action':'search',
		'dnf_opt_finalize':'1',
		'dnf_opt_mode':'update',
		'dnf_opt_target':'',
		'dnf_opt_validate':'1',
		'dnf_class_values[procurement_notice][dnf_class_name]':'procurement_notice',        
		'dnf_class_values[procurement_notice][keywords]': search_keywords,
		'dnf_class_values[procurement_notice][naics_code][]': search_naics_code,
	}
	
	# Submitting form with Keyword and Getting the results html 
	response = requests.post(url,data=data,headers=headers)    
	
	if(response.status_code == 200):        
		soup = BeautifulSoup(response.content)                
		cols = ['Solicitation name','Solicitation number','Solicitation Type','Posted on date','Agency','Office','Location','Page Url',
				'Synopsis','Contracting Office Address Street','Contracting Office City','Contracting Office State','Contracting Office Zip Code',
				'Contracting Office Country','Place of Performance','Primary Point of Contact First Name','Primary Point of Contact Last Name',
				'Primary Point of Contact Title','Primary Point of Contact Email','Primary Point of Contact Phone','Primary Point of Contact Fax',
				'Secondary Point of Contact First Name','Secondary Point of Contact Last Name','Secondary Point of Contact Title','Secondary Point of Contact Email',
				'Secondary Point of Contact Phone','Secondary Point of Contact Fax','Original Posted Date','Posted Date','Response Date',
				'Original Response Date','Archive Policy','Original Archive Date','Archive Date','Original Set Aside','Set Aside','Watch This Opportunity',
				'Add Me To Interested Vendors','Packages Tab Link','Interested Vendors Tab Link']

		# Code for creating database if not exists
		db = MySQLdb.connect(host=Host, # your host, usually localhost
				 user=Username, # your username
				  passwd=Password, # your password
				  ) # name of the data base
		cur = db.cursor()
		
		try:
			cur.execute("CREATE DATABASE IF NOT EXISTS {0}".format(Database))
		except:
			print "Some Error Occurred"
			pass
		
		db = MySQLdb.connect(host=Host, # your host, usually localhost
				 user=Username, # your username
				  passwd=Password, # your password
				  db=Database) # name of the data base

		cur = db.cursor()

		query = """CREATE TABLE IF NOT EXISTS %s (
						solicitation_name               varchar(500), 
						solicitation_number             varchar(50),
						solicitation_type               varchar(300),
						posted_on_date                  Date,
						agency                          varchar(100),
						office                          varchar(100),
						location                        varchar(100),
						page_url                        varchar(100),
						synopsis                        text,
						contracting_office_street       varchar(100),
						contracting_office_city         varchar(100),
						contracting_office_state        varchar(60),
						contracting_office_zip          varchar(30),
						contracting_office_country      varchar(80),
						place_of_performance            text,
						primary_contact_fname           varchar(100),
						primary_contact_lname           varchar(100),
						primary_contact_title           varchar(100),
						primary_contact_email           varchar(100),
						primary_contact_phone           varchar(100),
						primary_contact_fax             varchar(100),
						secondary_contact_fname         varchar(100),
						secondary_contact_lname         varchar(100),
						secondary_contact_title         varchar(100),
						secondary_contact_email         varchar(100),
						secondary_contact_phone         varchar(100),
						secondary_contact_fax           varchar(100),
						original_posted_date            Date DEFAULT null,
						posted_date                     Date DEFAULT null,
						response_date                   Date DEFAULT null,
						original_response_date          Date DEFAULT null,
						archive_policy                  varchar(200),
						original_archive_date           Date DEFAULT null,
						archive_date                    Date DEFAULT null,
						original_set_aside              varchar(50),
						set_aside                       varchar(50),
						watch_opportunity_link          varchar(100),
						interested_vendors_link         varchar(100),                       
						packages_tab_link               varchar(100),
						interested_vendors_tab_link     varchar(100)

					)""" % Table
		# print query
			# break
			
		#Creating database table with Cols            
		try:
			cur.execute(query) 
		except:
			print "Some Error Occurred"
			pass  


		table_data = soup.find('table',{'class':'list'})
		listdata = []
		solicitation_name = solicitation_number = agency_office_location = posted_on_date = None
		for rowdata in table_data.find_all('tr'): 
			html = lxml.html.fromstring(str(rowdata))
		### BEGIN ERROR TEST CODE
			page_url2 = html.xpath('//td/a[@class="lst-lnk-notice"][1]/@href')            
			if page_url2:
				page_url2 = "https://www.fbo.gov/"+str(page_url2[0])
				print page_url2
		### END ERROR TEST CODE
			#Field1
			if rowdata.find('div',{'class':'solt'}):  
				solicitation_name = rowdata.find('div',{'class':'solt'}).getText()
				listdata.append([solicitation_name])                
			#Field 2
			if rowdata.find('div',{'class':'soln'}):
				solicitation_number = rowdata.find('div',{'class':'soln'}).getText()
				listdata.append([solicitation_number])     
			#Field 3    
			if html.xpath('//td[@headers="lh_base_type"]/text()'):
				solicitation_type = html.xpath('//td[@headers="lh_base_type"]/text()')
				solicitation_type = [loc.strip(' \n ') for loc in solicitation_type] 
				
				if solicitation_type:
					listdata.append(solicitation_type)     
			#Field 4
			if rowdata.find('td',{'class':'lst-cl-last'}):  
				posted_on_date = rowdata.find('td',{'class':'lst-cl-last'}).getText().strip()
				# posted_date  = re.sub('[\s]',' ',str(original_posted_date)).strip()
				if posted_on_date:
					posted_on_date_match = re.match('\w*\s\d\d\,\s\d{4}',posted_on_date)
					if posted_on_date_match:
						print posted_on_date_match.group()
						posted_on_date = parse(posted_on_date_match.group())

				listdata.append([posted_on_date])  
				# sys.exit(1)
			#Field 5
			if rowdata.find('div',{'class':'pagency'}):  
				agency = rowdata.find('div',{'class':'pagency'}).getText()                
				listdata.append([agency])     
				
			#Field 6,7
			if html.xpath('//td[@headers="lh_agency_name"]/text()'):
				office_and_location = html.xpath('//td[@headers="lh_agency_name"]/text()')
				office_and_location = [loc.strip(' \n ') for loc in office_and_location]                
				if office_and_location:
					office = office_and_location[1] 
					location = office_and_location[2]
					listdata.append([office])
					listdata.append([location])                                     
			
			#Field 8
			page_url = html.xpath('//td/a[@class="lst-lnk-notice"][1]/@href')            
			if page_url:
				page_url = "https://www.fbo.gov/"+str(page_url[0])           
				listdata.append([page_url])      
				# print page_url
				#Request for getting HTML of each page url
				response = urllib2.urlopen(page_url)
				if(response.code == 200):
					html = lxml.html.fromstring(''.join(response.read()))
					btn_links(html)
					#Field 9
					synopsis = html.xpath('//div[@id="so_formfield_dnf_class_values_procurement_notice__description_"]//text()')
					synopsis = ' '.join([re.sub('[\s]',' ',str(sa)).strip() for sa in synopsis]).replace('"',"'")
					listdata.append([synopsis]) 
					
					#Field 10 to 14
					listdata.append(contracting_office_info(html))
					# print contracting_office_info(html)
					#Field 15                    
					place_of_performance = html.xpath('//div[@id="dnf_class_values_procurement_notice__place_of_performance__widget"]/text()')
					place_of_performance = ' '.join(''.join([re.sub('[\s]',' ',info).strip() for info in place_of_performance]).split())                                    
					listdata.append([place_of_performance])
					#Field 16 to 21
					# print primary_point_of_contact(html)
					listdata.append(primary_point_of_contact(html))
					#Field 22 to 27
					print "Secondary info"
					if secondary_point_of_contact(html):
						listdata.append(secondary_point_of_contact(html))
					else:
						listdata.append([' ' for x in range(0,6)])
					# print secondary_point_of_contact(html)
					#Field 28 to 36
					listdata.append(general_information(html))
					print "General Information"
					print general_information(html)
					print "END General Information"
					# Field 37 to 40
					listdata.append(btn_links(html))
							
			listdata = [str(i) if i is not None else ' ' for item in listdata for i in item]
								
			# INSERTING values in db table
			insertquery = 'INSERT INTO {0} VALUES ("{1}")'.format(Table,'","'.join(listdata))                 
			# print '","'.join(listdata)
			print insertquery

			try:
				cur.execute(insertquery) 
				db.commit()
			except MySQLdb.Error as e:
				print e
				print "Some error occured"
				pass  

			#Empty list after each iteration            
			del listdata[:]


### Original Code
# extract("https://www.fbo.gov/index?s=opportunity&tab=search&mode=list")

### Revised Code
###  Original Search Terms:   extract("https://www.fbo.gov/index?s=opportunity&tab=search&mode=list",'solar','0025021')
search_naics_codes = ['0025007','0025021']
extract("https://www.fbo.gov/index?s=opportunity&tab=search&mode=list",'solar',search_naics_codes)
