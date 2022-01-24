import json
import requests
import argparse
import re
import copy


#Load a json file and ready it for action extraction
def load_file(file):
    json_file = open(file)
    json_data = json.load(json_file)
    
    return json_data

#Get the http request and receive a response
def http_request_action(the_url, url_params=None):
    if url_params is not None:
        the_url_response = requests.get(the_url, url_params)
    else:
        the_url_response = requests.get(the_url)
    
    return the_url_response

#get all actions in the json file that will be executed
def get_action_rules(json_data):
    action_list = []
    for it in range(len(json_data['actions'])):
        action_list.append(json_data['actions'][it])    
    return action_list


#parse the output depending onthe type of action
#Works for bothurl and messages
def output_parser(url, action_events):
    pattern = "\{[^}]*\}\}"
    output_p = []
   
    #find the parameters in the url or message if any. If there isn't, return the url or message. 
    v_params = re.findall(pattern,url)
    if len(v_params) > 0:
        #save a copy of the parameters
        params = copy.deepcopy(v_params)
        #strip the curly braces and split the value into key & values
        for i in range(len(params)):
            params[i]=params[i].replace('{','')
            params[i]=params[i].replace('}','')
            params[i]=params[i].split('.')

        #get param value from action events dictionary if it exists
        #slight issue here, the code is not dynamic for dictionary nesting 
        # fixed below
        for param in params:
            action_value = action_events
            for l in range(len(param)):
                try:    
                    action_value = action_value[param[l]]
                except KeyError:
                    action_value = ""
                    break
            output_p.append(action_value)
         
            '''
            if len(param) == 2:
                try:
                    output_p.append(action_events[param[0]][param[1]])
                except KeyError:
                    output_p.append("")
            elif len(param) == 3:
                try:
                    output_p.append(action_events[param[0]][param[1]][param[2]])
                except KeyError:
                    output_p.append("")
            elif len(param) == 4:
                try:
                    output_p.append(action_events[param[0]][param[1]][param[2]][param[3]])
                except KeyError:
                    output_p.append("")
            '''
            
                
        #zip param with its value for substitution
        zip_p = zip(v_params, output_p)
        zip_d = dict(zip_p)

        #rebuild url or message
        built_url = copy.deepcopy(url)
        for a, b in zip_d.items():
            built_url = built_url.replace(a,str(b))
        return built_url
    else:
        return url

    
#run each action in the json file by getting the appropriate url 
#or printing the appropriate message
def rule_manager(action_rules, action_events,json_data):
    output_to_print = []
    for ind, rule in enumerate(action_rules):
        #print("rule is :",rule)
        
        if rule['type'] == 'HTTPRequestAction':
            action_url = rule['options']['url']
            parsed_url = output_parser(action_url, action_events)
            url_response = http_request_action(parsed_url)
            url_dict = url_response.json()
            action_events[rule['name']] = url_dict
        elif rule['type'] == 'PrintAction':
            action_msg = rule['options']['message']
            parsed_msg = output_parser(action_msg, action_events)
            action_events[rule['name']] = parsed_msg
            output_to_print.append(action_events[rule['name']])
        else:
            print("Invalid action")
    
    return output_to_print        
    
def main():
    
    #receive file from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("-file", "--file", help = "Enter json file")

    args = parser.parse_args()
    file = args.file
    print(file)
    
    json_data = load_file(file)
    
    action_rules = get_action_rules(json_data)
    action_events = {}
    action_output = rule_manager(action_rules, action_events, json_data)
    
    for output in action_output:
        print(output)
    
    
    
    
if __name__ == '__main__':
    main()
    
            


    
    
