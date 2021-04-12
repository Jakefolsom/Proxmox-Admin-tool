import requests
import json
import datetime
import time
import re
'''
gets a dict from settings
makes ticket request
returns dict with ticket and csrf token to be used later
{ticket: '...', CSRF: '...'}

'''
def getTicketandCSRF(settings):
	data = {
	  'username': settings['user']+'@'+settings['realm'],
	  'password': settings['pass']
	}

	response = requests.post('https://'+settings['URL'] +'/api2/json/access/ticket', data=data, verify=False)
	parser = response.json()
	return {"ticket": parser['data']['ticket'], "CSRF": parser['data']['CSRFPreventionToken'], "URL": settings['URL'] }


'''
takes dict generated from getTicketandCSRF, dict of accountSettings
accountSettings must match this:
{
	'baseUsername': '...',
	'defaultPassword': '...',
	'expires': '', (Year, month, day format)
	'numberOfAccounts': '..',
	'realm': '..'

}

take expires and translates to epoch time

runs a loop for accountSettings['numberOfAccounts']

returns value "Done" 

'''
def massCreateUser(ticketandCSRF, accountSettings):
	
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']} 
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']} 
	timestruct = time.strptime(accountSettings['expires'], "%Y-%m-%d")
	epochTime = str(int(time.mktime(timestruct)))
	for user in range(1,int(accountSettings["numberOfAccounts"])+1):
		r=requests.post("https://"+ticketandCSRF['URL']+"/api2/json/access/users", data={"userid": accountSettings['baseUsername']+str(user)+'@'+accountSettings['realm'], "password": accountSettings['defaultPassword'], "expire": epochTime}, cookies=cookies, headers=headers, verify=False)




def massDeletionUsers(ticketandCSRF, accountSettings):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	for user in range(1,int(accountSettings["numberOfAccounts"])+1):
		url = "https://"+ticketandCSRF['URL']+"/api2/json/access/users/"+accountSettings['baseUsername']+str(user)+'@'+accountSettings['realm']
		r=requests.delete(url, cookies=cookies, headers=headers, verify=False)




'''
takes dict generated from getTicketandCSRF, dict of accountSettings
accountSettings must match this:
{
	'baseUsername': '...',
	'numberOfAccounts': '...',
	'startingVMNumber': '..',
	'EndingVMNumber': '..',
	'realm': '..',
	'role': '...'

}

'''
def massAddUserToVM(ticketandCSRF,accountSettings):
	if accountSettings['numberOfAccounts'] != str((int(accountSettings['EndingVMNumber']) - int(accountSettings['startingVMNumber']))+1):
		return "NumberMissMatch"
	else:
		headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
		cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
		counter = 0
		for user in range(1,int(accountSettings["numberOfAccounts"])+1):
			url = "https://"+ticketandCSRF['URL']+"/api2/extjs/access/acl"
			data = {'path': "/vms/"+str(int(accountSettings['startingVMNumber'])+counter), 'users': accountSettings['baseUsername'] + str(user) +'@'+ accountSettings['realm'] , 'roles': accountSettings['role']}
			r=requests.put(url, params= data, cookies=cookies, headers=headers, verify=False)
			counter = counter+1

def massRemoveUserFromVM(ticketandCSRF,accountSettings):
	if accountSettings['numberOfAccounts'] != str((int(accountSettings['EndingVMNumber']) - int(accountSettings['startingVMNumber']))+1):
		return "NumberMissMatch"
	else:
		headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
		cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
		counter = 0
		for user in range(1,int(accountSettings["numberOfAccounts"])+1):
			url = "https://"+ticketandCSRF['URL']+"/api2/extjs/access/acl"
			data = {'delete': '1', 'path': "/vms/"+str(int(accountSettings['startingVMNumber'])+counter), 'users': accountSettings['baseUsername'] + str(user) +'@'+ accountSettings['realm'] , 'roles': accountSettings['role']}
			r=requests.put(url, params= data, cookies=cookies, headers=headers, verify=False)
			counter = counter+1

def getRoles(ticketandCSRF):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	url = "https://"+ticketandCSRF['URL']+"/api2/json/access/roles"
	r = requests.get(url,cookies=cookies, headers=headers, verify=False)
	toParse = r.json()
	return [d["roleid"] for d in toParse['data']]



