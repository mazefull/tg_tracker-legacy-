import json
import paramiko
import os

ndir = os.getcwd()
os.chdir(f"{ndir}\\modules\\mods\\vpn_vps_worker")
print(os.getcwd())

with open("settings.json", "r", encoding="utf-8") as settings:
    data = json.load(settings)

mode = data["setup"]["mode"]
host = data["setup"]["vps"]["host"]  # ip
user = data["setup"]["vps"]["user"]  # login
secret = data["setup"]["vps"]["secret"]  # pswd
port = data["setup"]["vps"]["port"]
admin_id = data["setup"]["tbot"]["admin_id"]
operator_ids = data["setup"]["tbot"]["operator_ids"].split(",")
bot_api = data["setup"]["tbot"]["API"]


def vps_remote_getprofile(profile_name, ids):
    if os.path.exists('ovpn_profiles'):
        pass
    else:
        os.system('mkdir ovpn_profiles')
    transport = paramiko.Transport((host, int(port)))
    transport.connect(username=user, password=secret)
    sftp = paramiko.SFTPClient.from_transport(transport)
    remotepath = f'{profile_name}.ovpn'
    localpath = f'ovpn_profiles\{profile_name}.ovpn'
    sftp.get(remotepath, localpath)
    sftp.close()
    transport.close()
    if os.path.exists(f'ovpn_profiles\\{profile_name}.ovpn'):
        return True
    else:
        return False

def vps_remote_paramiko(profile_name, ids):
    print("START_PARAMIKO")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=secret, port=port)
    comm = f'MENU_OPTION="1" CLIENT="{profile_name}" PASS="1" ./openvpn-install.sh'
    stdin, stdout, stderr = client.exec_command(comm)
    data = stdout.read() + stderr.read()
    print(data)
    client.close()
    return vps_remote_getprofile(profile_name, ids)


def vps_new_profile(profile_name, ids):
    payload = f'MENU_OPTION="1" CLIENT="{profile_name}" PASS="1" ./openvpn-install.sh'
    if mode == 'vps':
        if os.path.exists('openvpn-install.sh'):
            print('OVPN SHELL EXISTS')
        else:
            os.system('git clone https://github.com/angristan/openvpn-install.git')
            os.system('cp openvpn-install/openvpn-install.sh ./openvpn-install.sh')
            print('OVPN SHELL INSTALLED')
        os.system(payload)
        os.system(f'mv ../{profile_name}.ovpn ./{profile_name}.ovpn' )

    else:
        return vps_remote_paramiko(profile_name, ids)
    print('_vpn')