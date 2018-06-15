###
#
# Lenovo Redfish examples - set_bios_bootmode_legacy
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


import json, sys
import redfish
import lenovo_utils as utils


def set_bios_bootmode_legacy(ip, login_account, login_password, system_id):
    result = {}
    login_host = "https://" + ip
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
        # Example: bios_attributes = {\"name\":\"value\"}
        attributes = {}
        attributes['bios_attr_name'] = "BootSourceOverrideMode"
        attributes['bios_attr_value'] = "Legacy"
        bios_attributes = "{\"" + attributes['bios_attr_name'] + "\":\"" + attributes['bios_attr_value'] + "\"}"

        parameter = {"Boot": json.loads(bios_attributes)}
        response_system_url = REDFISH_OBJ.patch(system_url, body=parameter)

        if response_system_url.status == 200:
            result = {'ret': True, 'msg': 'set bios bootmode legacy successful'}
        elif response_system_url.status == 400:
            result = {'ret': False, 'msg': 'Not supported on this platform'}
        elif response_system_url.status == 405:
            result = {'ret': False, 'msg': "Resource not supported"}
        else:
            result = {'ret': False, 'msg': "set bios bootmode legacy failed"}
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
    result = set_bios_bootmode_legacy(ip, login_account, login_password, system_id)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])