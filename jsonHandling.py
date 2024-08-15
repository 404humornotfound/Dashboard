import json

def get_secure_info():
    f = open('secret_ids.json')
    data = json.load(f)
    f.close()
    return data['info_gid'], data['sheet_id'], data['sheet_name']
