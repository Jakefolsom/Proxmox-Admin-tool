from flask import Flask, render_template, send_from_directory, request
from flaskwebgui import FlaskUI #get the FlaskUI class
import os
import json
import pyAesCrypt
import userTools as userTool
import datetime
import vmTools as vmTool
app = Flask(__name__, static_folder='static')  

# Feed it the flask app instance 
ui = FlaskUI(app)
settings = []
@app.route("/")
def index():
    try:
        f = open("settings.json.JFC")
        return render_template("lockScreen.html")
    except:
        return render_template("index.html")
@app.route("/unlock", methods=['GET', 'POST'])
def unlock():
    if request.method == 'POST':
        password = request.form['password']
        try:
            bufferSize = 64 * 1024
            pyAesCrypt.decryptFile("settings.json.JFC", "settings.json", password, bufferSize)
            global GlobPass 
            GlobPass = password
        except:
            return render_template("lockScreen.html", status="BadPass")
        with open("settings.json") as file:
            global settings
            settings = json.load(file)
        os.remove("settings.json.JFC")
        return render_template("index.html")
@app.route("/home")
def home():
    return render_template("index.html")
@app.route("/lock", methods=['GET', 'POST'])
def lock():
    try:
        if GlobPass:
            bufferSize = 64 * 1024
            password = GlobPass
            pyAesCrypt.encryptFile("settings.json", "settings.json.JFC", password, bufferSize)
            os.remove("settings.json")
            return render_template("lockScreen.html")
        return render_template("settings.html")
 
    except:
        return render_template("settings.html")
@app.route("/users")
def users():
    return render_template("userPage.html")
@app.route("/massUserDeletion", methods=['GET', 'POST'])
def deleteMassUsers():
    if request.method == 'POST':
        accountSettings = {
            'baseUsername': request.form['baseUsername'],
            'numberOfAccounts': request.form['numberOfAccounts'],
            'realm': request.form["realm"]
        }
        if len(request.form["baseUsername"]) == 0:
            return render_template("massUserDeletion.html", status="emptyBaseUserName", info=accountSettings)
        elif len(request.form["numberOfAccounts"]) == 0 or isinstance(request.form['numberOfAccounts'], int):
            return render_template("massUserDeletion.html", status="badNumberOfAccounts", info=accountSettings)
        elif len(request.form["realm"]) == 0:
            print("bad realm")
            return render_template("massUserDeletion.html", status="badRealm", info=accountSettings)
        else:
            userTool.massDeletionUsers(userTool.getTicketandCSRF(settings), accountSettings)
            return render_template("massUserDeletion.html", status="success")
    
    return render_template("massUserDeletion.html")

@app.route("/massUserCreation", methods=['GET','POST'])
def createMassUsers():
    regex = datetime.datetime.strptime
   
    if request.method == 'POST':
        accountSettings = {
                            'baseUsername': request.form["baseUsername"],
                            'defaultPassword': request.form["defaultPassword"],
                            'expires': request.form["expiresDate"], #(Year, month, day format)
                            'numberOfAccounts': request.form["numberOfAccounts"],
                            'realm': request.form["realm"]

                        }
        try:
            assert regex(request.form["expiresDate"], '%Y-%m-%d')
            dateCorrect = True
        except:
            dateCorrect = False

        if len(request.form["baseUsername"]) == 0:
            print("bad username")
            return render_template("massUserCreation.html", status="emptyBaseUserName", info=accountSettings)
        elif len(request.form["defaultPassword"]) < 4:
            print("bad password")
            return render_template("massUserCreation.html", status="shortPassword", info=accountSettings)
        elif not dateCorrect:
            print("bad datetime")
            return render_template("massUserCreation.html", status="badDateFormat", info=accountSettings)
        elif len(request.form["numberOfAccounts"]) == 0 or request.form["numberOfAccounts"] == '0':

            return render_template("massUserCreation.html", status="badNumberOfAccounts", info=accountSettings)
        elif len(request.form["realm"]) == 0:
            print("bad realm")
            return render_template("massUserCreation.html", status="badRealm", info=accountSettings)

        else:
            userTool.massCreateUser(userTool.getTicketandCSRF(settings), accountSettings)
            return render_template("massUserCreation.html", status="success")
    return render_template("massUserCreation.html")
@app.route("/vmTools", methods=['GET', 'POST'])
def vmtools():
    return render_template("vmTools.html")
@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        URL = request.form['URL']
        masterPass = request.form['masterPass']
        realm = request.form['realm']
        settings_JSON = {'URL': URL,
        'user': username,
        'pass': password,
        'realm': realm
        }
        with open("settings.json", "w") as f:
            f.write(json.dumps(settings_JSON, indent = 4, sort_keys=True))
        bufferSize = 64 * 1024
        GlobPass = masterPass
        pyAesCrypt.encryptFile("settings.json", "settings.json.JFC", GlobPass, bufferSize)
        os.remove("settings.json")
        return render_template("settings.html")
    return render_template('settings.html')
@app.route("/deleteSettings", )
def deleteSettings():
    os.remove("settings.json.JFC")
    return render_template('index.html')
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder,'image.ico', mimetype='image/vnd.microsoft.icon')



@app.route("/massAddUser", methods=["GET", "POST"])
def massAddUser():
    activeRoles = userTool.getRoles(userTool.getTicketandCSRF(settings))
    if request.method == 'POST':
        accountSettings = {
            'baseUsername': request.form["baseUsername"],
            'EndingVMNumber': request.form["EndingVMNumber"],
            'startingVMNumber': request.form["startingVMNumber"], 
            'numberOfAccounts': request.form["numberOfAccounts"],
            'role': request.form["role"],
            'realm': request.form["realm"]
            }
        if len(request.form["baseUsername"]) == 0:
            print("bad username")
            return render_template("massAddUser.html", status="emptyBaseUserName", info=accountSettings, length= len(activeRoles),roles= activeRoles)
        elif len(request.form["EndingVMNumber"]) < 0:
            print("bad EndingVMNumber")
            return render_template("massAddUser.html", status="badEndingVM", info=accountSettings,length= len(activeRoles),roles= activeRoles)
        elif len(request.form["startingVMNumber"]) < 0:
            print("bad startingVMNumber")
            return render_template("massAddUser.html", status="BadstartingVMNumber", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        elif len(request.form["numberOfAccounts"]) == 0 or request.form["numberOfAccounts"] == '0':
            return render_template("massAddUser.html", status="badNumberOfAccounts", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        elif len(request.form["realm"]) == 0:
            print("bad realm")
            return render_template("massAddUser.html", status="badRealm", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        elif len(request.form["role"]) == 0:
            print("bad role")
            return render_template("massAddUser.html", status="badrole", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        
        else:
            userTool.massAddUserToVM(userTool.getTicketandCSRF(settings), accountSettings)
            return render_template("massAddUser.html", status="success", length= len(activeRoles), roles=activeRoles)

    
    return render_template("massAddUser.html", length= len(activeRoles), roles= activeRoles)
@app.route("/massRemoveUser", methods=['GET', 'POST'])
def massRemoveUser():
    activeRoles = userTool.getRoles(userTool.getTicketandCSRF(settings))
    if request.method == 'POST':
        accountSettings = {
            'baseUsername': request.form["baseUsername"],
            'EndingVMNumber': request.form["EndingVMNumber"],
            'startingVMNumber': request.form["startingVMNumber"], 
            'numberOfAccounts': request.form["numberOfAccounts"],
            'role': request.form["role"],
            'realm': request.form["realm"]
            }
        if len(request.form["baseUsername"]) == 0:
            print("bad username")
            return render_template("massRemoveUser.html", status="emptyBaseUserName", info=accountSettings, length= len(activeRoles),roles= activeRoles)
        elif len(request.form["EndingVMNumber"]) < 0:
            print("bad EndingVMNumber")
            return render_template("massRemoveUser.html", status="badEndingVM", info=accountSettings,length= len(activeRoles),roles= activeRoles)
        elif len(request.form["startingVMNumber"]) < 0:
            print("bad startingVMNumber")
            return render_template("massRemoveUser.html", status="BadstartingVMNumber", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        elif len(request.form["numberOfAccounts"]) == 0 or request.form["numberOfAccounts"] == '0':
            return render_template("massRemoveUser.html", status="badNumberOfAccounts", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        elif len(request.form["realm"]) == 0:
            print("bad realm")
            return render_template("massRemoveUser.html", status="badRealm", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        elif len(request.form["role"]) == 0:
            print("bad role")
            return render_template("massAddUser.html", status="badrole", info=accountSettings,length= len(activeRoles), roles= activeRoles)
        
        else:
            userTool.massRemoveUserFromVM(userTool.getTicketandCSRF(settings), accountSettings)
            return render_template("massRemoveUser.html", status="success", length= len(activeRoles), roles=activeRoles)
    
    return render_template("massRemoveUser.html", length= len(activeRoles), roles= activeRoles)         

@app.route("/massVMClone", methods=['GET', 'POST'])
def massVMClone():
    templateDict = vmTool.getTemplates(vmTool.getTicketandCSRF(settings))
    if request.method == 'POST':

        accountSettings ={
        'node': vmTool.getVMID(vmTool.getTicketandCSRF(settings), request.form['template'])['node'],
        'ostemplate': str(vmTool.getVMID(vmTool.getTicketandCSRF(settings), request.form['template'])['vmid']), #NumberOfTemplate
        'newName': request.form['newName'], #counter will be added to end of string
        'numberOfvms': request.form['numberOfvms'],
        'newid': request.form['newid']
        }
        print(accountSettings)
        if len(accountSettings['newName']) == 0:
            return render_template("massVMcloning.html" ,templateDictLength= int(templateDict['totalTemplates']),templateDict=templateDict, status="badNewVMName", info=accountSettings)
        elif len(accountSettings['numberOfvms']) == 0 or accountSettings['numberOfvms'] == '0':
            return render_template("massVMcloning.html" ,templateDictLength= int(templateDict['totalTemplates']),templateDict=templateDict, status="badnumberOfvms", info=accountSettings)
        elif vmTool.searchForVMID(vmTool.getTicketandCSRF(settings), accountSettings['newid']) == 'found':
            return render_template("massVMcloning.html" ,templateDictLength= int(templateDict['totalTemplates']),templateDict=templateDict, status="badnewid", info=accountSettings)
        else:
            vmTool.createVM(vmTool.getTicketandCSRF(settings),accountSettings)
            return render_template("massVMcloning.html" , status="success" ,templateDictLength= int(templateDict['totalTemplates']),templateDict=templateDict, info=accountSettings)

    return render_template("massVMcloning.html" , templateDictLength= int(templateDict['totalTemplates']),templateDict=templateDict)

@app.route("/massVMDeletion", methods=['GET', 'POST'])
def massVMDeletion():
    if request.method == 'POST':
        try:
            if request.form['purge'] == 'on':
                if len( request.form['vmToDelete']) == 0:
                    return render_template("massVMDeletion.html", status="badvmToDelete")
                elif len(request.form['numberOfvms']) == 0:
                    return render_template("massVMDeletion.html", status="badnumberOfvms") 
                accountSettings = {
                    'node': vmTool.getNode(vmTool.getTicketandCSRF(settings), request.form['vmToDelete']),
                    'vmToDelete': request.form['vmToDelete'], #Starting vmid
                    'numberOfvms': request.form['numberOfvms'],
                    'purge': "1" #Check box
                }
        except:
            if len(request.form['vmToDelete']) == 0:
                    return render_template("massVMDeletion.html", status="badvmToDelete")
            elif len(request.form['numberOfvms']) == 0:
                return render_template("massVMDeletion.html", status="badnumberOfvms") 
            accountSettings = {
                'node': vmTool.getNode(vmTool.getTicketandCSRF(settings), request.form['vmToDelete']),
                'vmToDelete': request.form['vmToDelete'], #Starting vmid
                'numberOfvms': request.form['numberOfvms'],
                'purge': '0' #Check box
            }
        vmTool.deleteVM(vmTool.getTicketandCSRF(settings),accountSettings)
        return render_template("massVMDeletion.html", status="success")
    return render_template("massVMDeletion.html")


@app.route("/appendNetworkDevice", methods=['GET', 'POST'])
def appendNetworkDevice():
    if request.method == 'POST':
        if len(request.form['vmbrStartingNumber']) == 0:
            return render_template("appendNetworkDevice.html", status="badvmbrStartingNumber")
        elif len(request.form['interfaceName']) == 0:
            return render_template("appendNetworkDevice.html", status="badinterfaceName")
        elif len(request.form['vmid']) == 0:
            return render_template("appendNetworkDevice.html", status="badvmid")
        elif vmTool.getNode(vmTool.getTicketandCSRF(settings), request.form['vmid']) == "Not Found":
            return render_template("appendNetworkDevice.html", status="unknownVMID")
        try:
            if request.form['increment']:
                startingNumber = int(request.form['vmbrStartingNumber'])
                print(int(request.form['timesToRun']))
                vmid = request.form['vmid']
                for x in range(int(request.form['timesToRun'])):
                    print(str(x) + " Time through")
                    accountSettings = {
                        'vmid': vmid,
                        'vmbrStartingNumber': str(startingNumber),
                        'interfaceName': request.form['interfaceName'],
                        'node': vmTool.getNode(vmTool.getTicketandCSRF(settings), request.form['vmid'])
                    }
                    print(accountSettings)
                    vmTool.appendNetwork(vmTool.getTicketandCSRF(settings), accountSettings)
                    startingNumber =  startingNumber + 1
                    vmid = vmid + 1

        except:
            vmid = int(request.form['vmid'])
            for x in range(int(request.form['timesToRun'])):
                    accountSettings = {
                        'vmid': str(vmid),
                        'vmbrStartingNumber': request.form['vmbrStartingNumber'],
                        'interfaceName': request.form['interfaceName'],
                        'node': vmTool.getNode(vmTool.getTicketandCSRF(settings), request.form['vmid'])
                    }

                    vmTool.appendNetwork(vmTool.getTicketandCSRF(settings), accountSettings)
                    vmid = vmid + 1


    return render_template("appendNetworkDevice.html")
ui.run()