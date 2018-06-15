###
#
# Lenovo Redfish examples - Get the PSU information
#
# Copyright Notice:
#
# Copyright 2018 Lenovo Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
###


import sys
import redfish
import json
import lenovo_utils as utils


def get_psu_info(ip, login_account, login_password, system_id):
    result = {}
    psu_details = []
    login_host = 'https://' + ip
    try:
        # Connect using the BMC address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                             password=login_password, default_prefix='/redfish/v1')

        # Login into the server and create a session
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct"}
        return result
    # GET the ComputerSystem resource
    system = utils.get_system_url("/redfish/v1", system_id, REDFISH_OBJ)
    if not system:
        result = {'ret': False, 'msg': "This system id is not exist or system member is None"}
        REDFISH_OBJ.logout()
        return result
    for i in range(len(system)):
        system_url = system[i]
        response_system_url = REDFISH_OBJ.get(system_url, None)
        
        if response_system_url.status == 200:
            # Get the Chassis resource
            chassis_url = response_system_url.dict['Links']['Chassis'][0]['@odata.id']
            
        else:
          
            result = {'ret': False, 'msg': "response system url Error code %s" % response_system_url.status}
            REDFISH_OBJ.logout()
            return result
        response_chassis_url = REDFISH_OBJ.get(chassis_url, None)
        if response_chassis_url.status == 200:
            # Get the power_url_list
            power_url = response_chassis_url.dict['Power']['@odata.id']
        else:
            
            result = {'ret': False, 'msg': "response chassis url Error code %s" % response_chassis_url.status}
            REDFISH_OBJ.logout()
            return result
        response_power_url = REDFISH_OBJ.get(power_url, None)
        if response_power_url.status == 200:
            power_supply_list = response_power_url.dict['PowerSupplies']
            for PowerSupplies in power_supply_list:
                entry = {}
                name = PowerSupplies['Name']
                Serial_Number = PowerSupplies['SerialNumber']
                Part_Number = PowerSupplies['PartNumber']
                Firmware_Version = PowerSupplies['FirmwareVersion']
                Power_Capacity_Watts = PowerSupplies['PowerCapacityWatts']
                Power_Supply_Type = PowerSupplies['PowerSupplyType']
                Status = PowerSupplies['Status']['State']
                Health = PowerSupplies['Status']['Health']
                if 'Manufacturer' in PowerSupplies:
                    Manufacturer = PowerSupplies['Manufacturer']
                else:
                    Manufacturer = "None"
                
                entry['Name'] = name
                entry['SerialNumber'] = Serial_Number
                entry['PartNumber'] = Part_Number
                entry['FirmwareVersion'] = Firmware_Version
                entry['PowerCapacityWatts'] = Power_Capacity_Watts
                entry['PowerSupplyType'] = Power_Supply_Type
                entry['State'] = Status
                entry['Health'] = Health
                entry['Manufacturer'] = Manufacturer
                psu_details.append(entry)
        else:
            result = {'ret': False, 'msg': "response power url Error code %s" % response_power_url.status}
            REDFISH_OBJ.logout()
            return result

        result['ret'] = True
        result['entry_details'] = psu_details
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result


if __name__ == '__main__':
    # ip = '10.10.10.10'
    # login_account = 'USERID'
    # login_password = 'PASSW0RD'
    
    ip = sys.argv[1]
    login_account = sys.argv[2]
    login_password = sys.argv[3]
    try:
        system_id = sys.argv[4]
    except IndexError:
        system_id = None
    result = get_psu_info(ip, login_account, login_password, system_id)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entry_details'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])