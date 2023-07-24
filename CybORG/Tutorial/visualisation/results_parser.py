

"""
Parsing the OpenAI truth tables output from CAGE Challenge
- opens given results (.txt expected) file
- parses for fields at each step of training
- rights the results into a .json file (with the same name if one is not given)
- returns list of dictionaries containing (in order) the table contents for visualisation code

Expecting a format similar to:

----------------------------------------------------------------------------
Blue Action: 9
Reward: 0.0, Episode reward: 0.0
Network state:
Scanned column likely inaccurate.
+-----------------+--------------+-------------+-------+---------+------------+
|      Subnet     |  IP Address  |   Hostname  | Known | Scanned |   Access   |
+-----------------+--------------+-------------+-------+---------+------------+
|  10.0.138.16/28 | 10.0.138.28  |   Defender  | False |  False  |    None    |
|  10.0.138.16/28 | 10.0.138.27  | Enterprise0 | False |  False  |    None    |
|  10.0.138.16/28 | 10.0.138.17  | Enterprise1 | False |  False  |    None    |
|  10.0.138.16/28 | 10.0.138.24  | Enterprise2 | False |  False  |    None    |
| 10.0.212.128/28 | 10.0.212.134 |   Op_Host0  | False |  False  |    None    |
| 10.0.212.128/28 | 10.0.212.136 |   Op_Host1  | False |  False  |    None    |
| 10.0.212.128/28 | 10.0.212.140 |   Op_Host2  | False |  False  |    None    |
| 10.0.212.128/28 | 10.0.212.141 |  Op_Server0 | False |  False  |    None    |
|  10.0.151.96/28 | 10.0.151.102 |    User0    |  True |  False  | Privileged |
|  10.0.151.96/28 | 10.0.151.109 |    User1    |  True |  False  |    None    |
|  10.0.151.96/28 | 10.0.151.108 |    User2    |  True |  False  |    None    |
|  10.0.151.96/28 | 10.0.151.103 |    User3    |  True |  False  |    None    |
|  10.0.151.96/28 | 10.0.151.100 |    User4    |  True |  False  |    None    |
+-----------------+--------------+-------------+-------+---------+------------+
----------------------------------------------------------------------------
.


"""

# Detect encoding of the passed text file without chardet
# https://stackoverflow.com/questions/436220/how-to-determine-the-encoding-of-text
def detect_encoding(file_name):
    with open(file_name, 'rb') as f:
        rawdata = f.read(10)
    import codecs
    # check for known BOMs
    if rawdata.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    if rawdata.startswith(codecs.BOM_UTF16_LE):
        return 'utf-16le'
    if rawdata.startswith(codecs.BOM_UTF16_BE):
        return 'utf-16be'
    #check for UTF32
    if rawdata[4:8] == b'\x00\x00\x00\x00':
        return 'utf-32be'
    if rawdata[0:4] == b'\x00\x00\x00\x00':
        return 'utf-32le'
    # if no BOM found, check for non-printable characters
    if b'\x00' in rawdata:
        return 'utf-16le'
    # default
    return 'utf-8'

def parse_results(file_name, dest_file_name=""):
    # Detect the encoding
    encoding = detect_encoding(file_name)
    with open(file_name, 'r', encoding=encoding) as fp:
        lines = fp.readlines()
    results_json = []
    step = {"hosts":[]}
    header = False

    def add_step_to_results():
        # use the step variable from the outer scope
        nonlocal step
        if len(step["hosts"]):
            results_json.append(step)
            step = {"hosts":[]}
            
    for i in range(len(lines)):
        l = lines[i]
        if "Blue Action: " in l:
            # We arrived to a new step, add the previous step to the results
            add_step_to_results()
            step["blue_action"] = l.lstrip('Blue Action: ').strip()
    #         print(f"\'{blue_action}\'")
        if "Red Action: " in l:
            # We arrived to a new step, add the previous step to the results
            add_step_to_results()
            step["red_action"] = l.lstrip('Red Action: ').strip()
        elif "Reward: " in l:
            rewards = l.split(",")
            step["reward"] = rewards[0].lstrip("Reward: ")
            if len(rewards) > 1:
                step["ep_reward"] = rewards[1].strip().lstrip("Episode reward: ")
    #         print(f"parsed: {reward} and {ep_reward}")
        elif "+" in l:
            # check if we are not at the end of the file
            if i+1 < len(lines):
                if "Subnet" in lines[i+1]:
                    # We arrived to a new step, add the previous step to the results
                    add_step_to_results()
                    header = True
                else: # Header started so this is end of header
                    header = False
        elif not header and "|" in l:
            row = l.split("|")
            attr = {} # attributes listed by hostname
            attr["subnet"] = row[1].strip()
            attr["ip_addr"] = row[2].strip()
            attr["known"] = "True" in row[4].strip()
    #         print("True" in attr["known"])
            attr["scanned"] = "True" in row[5].strip()
            attr["access"] = row[6].strip()
            attr["hostname"] = row[3].strip()
            step["hosts"].append(attr)
    #         print(f"{hostname} ({ip_addr} with subnet {subnet}) is known ({known}), scanned ({scanned}), and access ({access})")
    #         print(row)
        elif "------------------------------------------" in l:
            # We arrived to a new step, add the previous step to the results
            add_step_to_results()
        else:
            continue

    # Add the previous step to the results if not already added
    add_step_to_results()
    if dest_file_name == "":
        dest_file_name = file_name.rstrip(".txt") + ".json"
    with open(dest_file_name, 'w') as fp:
        fp.write(str(results_json))
    return results_json












