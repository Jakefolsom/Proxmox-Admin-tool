import requests
import json
import datetime
import time
from urllib.parse import quote

def getTicketandCSRF(settings):
	data = {
	  'username': settings['user']+'@'+settings['realm'],
	  'password': settings['pass']
	}

	response = requests.post('https://'+settings['URL'] +'/api2/json/access/ticket', data=data, verify=False)
	parser = response.json()
	return {"ticket": parser['data']['ticket'], "CSRF": parser['data']['CSRFPreventionToken'], "URL": settings['URL'] }




def createVM(ticketandCSRF, vmSettings):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	timesrun=0
	for user in range(1,int(vmSettings["numberOfvms"])+1):
		url = "https://"+ticketandCSRF['URL']+"/api2/json/nodes/"+vmSettings['node']+"/qemu/"+vmSettings['ostemplate']+"/clone?target="+vmSettings['node']+'&newid='+str(int(vmSettings['newid'])+timesrun)+'&name='+vmSettings['newName']+str(timesrun+1)
		r=requests.post(url, cookies=cookies, headers=headers, verify=False)
		timesrun = timesrun+1

def deleteVM(ticketandCSRF, vmSettings):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	timesrun=0
	for user in range(1,int(vmSettings["numberOfvms"])+1):
		if vmSettings['purge'] == '1':
			url = "https://"+ticketandCSRF['URL']+"/api2/json/nodes/"+vmSettings['node']+"/qemu/"+str(int(vmSettings['vmToDelete'])+timesrun)+'?purge=1'
		else:
			url = "https://"+ticketandCSRF['URL']+"/api2/json/nodes/"+vmSettings['node']+"/qemu/"+str(int(vmSettings['vmToDelete'])+timesrun)
		r=requests.delete(url, cookies=cookies, headers=headers, verify=False)
		timesrun = timesrun+1

'''
This is needed to get the sha1 of the config file to prevent double writing
this function will return the digest from the current config file
https://192.168.180.10:8006/api2/extjs/nodes/pve2/qemu/100/config?_dc=1609298139006
'''
def getDigest(ticketandCSRF, vmSettings):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	url = "https://"+ticketandCSRF['URL']+"/api2/extjs/nodes/"+vmSettings['node']+"/qemu/"+vmSettings['vmid']+"/config?_dc="+str(int(time.time()))
	r=requests.get(url, cookies=cookies, headers=headers, verify=False)
	parser = r.json()
	grossnet0 = parser['data'][vmSettings['interfaceName']]
	#since this is a gross string lets make it a dict for ease of use
	prettyNet0 = dict(subString.split("=") for subString in grossnet0.split(","))
	return {'digest': parser['data']['digest'], 'virtio': prettyNet0['virtio'], 'bridge': prettyNet0['bridge'], 'firewall': prettyNet0['firewall'] }  

'''
appends or changes network device. Takes 
vmSettings = {
	"interfaceName",
	"vmbrStartingNumber",

}

makes call to getDigest function which returns
dict that holds 
{
	"virtio",
	"firewall",
	"digest"

}
digest is the hash of the config file for said vm.
'''
def appendNetwork(ticketandCSRF,vmSettings):
	oldNetworkConfig = getDigest(ticketandCSRF, vmSettings)
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	data = vmSettings['interfaceName']+"="+quote("virtio=" +oldNetworkConfig['virtio']+",bridge=vmbr"+vmSettings['vmbrStartingNumber']+",firewall="+ oldNetworkConfig['firewall'])+"&digest="+oldNetworkConfig['digest']
	url = "https://"+ticketandCSRF['URL']+"/api2/json/nodes/"+vmSettings['node']+"/qemu/"+vmSettings['vmid']+"/config?"+data
	r=requests.post(url ,cookies=cookies, headers=headers, verify=False)


def getTemplates(ticketandCSRF):
	templateDict = {'totalTemplates': '0', 'data': []}
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	url = "https://"+ticketandCSRF['URL']+"/api2/json/cluster/resources"
	r=requests.get(url, cookies=cookies, headers=headers, verify=False)
	r = r.json()
	for i in range(0,len(r['data'])):
		try:
			if r['data'][i]['template'] == 1:
				templateDict['data'].append({'vmid':r['data'][i]['vmid'], 'name':r['data'][i]['name'], 'node':r['data'][i]['node']})
				templateDict['totalTemplates'] = str(int(templateDict['totalTemplates'])+1)
		except: 
			#ignore
			1+1
	return templateDict

def getVMID(ticketandCSRF, name):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	url = "https://"+ticketandCSRF['URL']+"/api2/json/cluster/resources"
	r=requests.get(url, cookies=cookies, headers=headers, verify=False)
	r = r.json()
	for i in range(0,len(r['data'])):
		try:
			if r['data'][i]['name'] == name:
				return { 'vmid': r['data'][i]['vmid'], 'node':r['data'][i]['node'] }
		except: 
			#ignore
			1+1
	return "Not Found"

def getNode(ticketandCSRF, name):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	url = "https://"+ticketandCSRF['URL']+"/api2/json/cluster/resources"
	r=requests.get(url, cookies=cookies, headers=headers, verify=False)
	r = r.json()
	for i in range(0,len(r['data'])):
		try:
			if r['data'][i]['vmid'] == int(name):
				return r['data'][i]['node'] 
		except: 
			#ignore
			1+1
	return "Not Found"

def searchForVMID(ticketandCSRF, name):
	headers = {'CSRFPreventionToken': ticketandCSRF['CSRF']}
	cookies = {'PVEAuthCookie': ticketandCSRF['ticket']}
	url = "https://"+ticketandCSRF['URL']+"/api2/json/cluster/resources"
	r=requests.get(url, cookies=cookies, headers=headers, verify=False)
	r = r.json()
	for i in range(0,len(r['data'])):
		try:
			print(r['data'][i]['vmid'])
			if r['data'][i]['vmid'] == int(name):
				return 'found'
		except: 
			#ignore
			1+1
	return "not found"