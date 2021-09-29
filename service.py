import napalm
from napalm_ros import ros
import pickle
import requests
import time

router_ip = '192.168.56.2'
router_port = 8728 # Use 8729 for api-ssl
router_user = 'admin'
router_pass = ''
file_name = 'file.txt'
token = '2SzBXxfaeNDp'
url = "http://localhost/managx/api/reports"

print("hello world")

driver = napalm.get_network_driver('ros')

print('Connecting to', router_ip, "on port", router_port, "as", router_user)

device = driver(hostname=router_ip, username=router_user,
                    password=router_pass, optional_args={'port': router_port})

def connection():
    # Use the RouterOS (ros) network driver to connect to the device:
    print('Opening ...')
    try:
        device.open()
        print('it is openned ...')
        get_addresses()
    except:
        print("Router is not up")

        params={
            'token': token
        }
        # resp = requests.post(url,data=params)
        # text =resp.text
        # print(text)

def get_addresses():
    arptable = device.get_arp_table()

    address = []

    connected_devices = []
    disconnected_devices = []
    changed_devices = []

    for entry in arptable:
        print(entry)

        address.append(entry)

    temp_list = read_file()

    # check if address is connecting
    for i in address:
        if i not in temp_list:
            
            obj = {
                'mac': i['mac'],
                'status': 'connected'
            }
            connected_devices.append(obj)
    
    # check if address is disconneted
    for i in temp_list:
        if i not in address:
        
            obj = {
                'mac': i['mac'],
                'status': 'disconnected'
            }
            disconnected_devices.append(obj)

    changed_devices = connected_devices + disconnected_devices
    print("this are the devices: {}".format(connected_devices))
    
    if len(changed_devices)>0:
        write_data(address)
        transfer_data(changed_devices)
        

def transfer_data(data):

    for i in data:
        parms = {
            'mac':i['mac'],
            'status': i['status'],
            'token': token
        }
        
        resp = requests.post(url,data=parms)
        text =resp.text
        print(text)


def write_data(sample_list):
    open_file = open(file_name, "wb")
    pickle.dump(sample_list, open_file)
    open_file.close()

def read_file():
    try:
        open_file = open(file_name, "rb")
        loaded_list = pickle.load(open_file)
        open_file.close()
    except EOFError:
        loaded_list = []

    return loaded_list

def start():    
    while(1):
        time.sleep(30)
        connection()
        
start()