#!/usr/bin/python2.7
import json, urllib, base64, re, requests, os, consul
from akamai.edgegrid import EdgeGridAuth
from urlparse import urljoin

consulhost = os.environ['CONSUL_HOST']
consulport = os.environ['CONSUL_PORT']
consulscheme = os.environ['CONSUL_SCHEME']
configsID = os.environ['CONNECTORID'] #available in Luna in the SIEM connector configuration section
###### Data for the Open API ######
open_client_token = os.environ['EG_CLIENT_TOKEN']
open_client_secret = os.environ['EG_CLIENT_SECRET']
open_access_token = os.environ['EG_ACCESS_TOKEN']
baseurl = os.environ['EG_BASE_URL']
###### End Of Main variable to be changed ######

consul_offset_key = 'dsztykma-logstash-siem/'+configsID+'/offset'

#Read offset value in the text file to be used in the API request
c = consul.Consul(host=consulhost, port=consulport, scheme=consulscheme)
index, offset = c.kv.get(consul_offset_key)
try:
    offset_value = offset["Value"]
except:
    offset_value = "null"

#Open API Authentication and request
s = requests.Session()
s.auth = EdgeGridAuth(
    client_token = open_client_token,
    client_secret = open_client_secret,
    access_token = open_access_token
)
path = '/siem/v1/configs/' + configsID +'?limit=1000&offset=' +offset_value

result = s.get(urljoin(baseurl,path),timeout=5, stream = True)

# If API call is a success, parse the result and split the attackData, store the resulting json in the logger created earlier
if result.status_code == 200:
    # Get a JSON string for a SIEM event:
    for line in result.iter_lines():
        event = json.loads(line)
        if "attackData" in event:
            attack_section = event['attackData']
            rules_array = []
            for member in attack_section:
                if member[0:4] != 'rule': continue
                member_as_singular = re.sub("s$", "", member)
                url_decoded = urllib.unquote(attack_section[member]).decode('utf8')
                url_decoded = re.sub(";$","",url_decoded)
                url_decoded = re.sub(";$","",url_decoded)
                member_array = url_decoded.split(";")
                if not len(rules_array):
                    for i in range(len(member_array)):
                        rules_array.append({})
                i = 0
                for item in member_array:
                    bits = base64.b64decode(item)
                    rules_array[i][member_as_singular] = unicode(bits, errors="replace")
                    i += 1
                    
            attack_section.pop('ruleMessages', None)
            attack_section.pop('ruleSelectors', None)
            attack_section.pop('rules', None)
            attack_section.pop('ruleActions', None)
            attack_section.pop('ruleVersions', None)
            attack_section.pop('ruleData', None)
            attack_section.pop('ruleTags', None)
            attack_section['rules'] = rules_array
            event['attackData'] = attack_section
            print(json.dumps(event, ensure_ascii=True))
        #update offset ID from the JSON response
        else:
            c.kv.put(consul_offset_key, event['offset'])
#If the API call fails then put null value in the offset file
else:
   None