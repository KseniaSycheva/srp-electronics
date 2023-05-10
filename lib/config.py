import json
import sys

def get_deployment_timer():
    '''
    Very simple method that reads a certain key from a JSON file that is stored on the feather
    in this case it is looking for the "deployment_delay_in_miliseconds" key
    There is no exception catching as the board should crash out when the config is not complete
    '''
    parsed_jsondata = json.loads(open('config.json', 'r').read())
    delay = parsed_jsondata['deployment_delay_in_miliseconds']

    return delay

