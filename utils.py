def add_attachment(revision, file_path, file_name):

    import requests
    
    url = "https://{domain}/api/publishing/v1/revision/{view_id}/{revision_seq}/attachment".format(
        view_id = revision.attributes['fourfour'],
        revision_seq = revision.attributes['revision_seq'],
        domain = revision.auth.domain
    )
    
    if isinstance(file_path, str):
        file = open(file_path, 'rb').read()
    else:
        file = file_path
    
    headers = {
        "x-file-name": file_name
    }

    req = requests.post(url=url,auth=revision.auth.basic, data=file, headers=headers)
    req.raise_for_status()
    file_info = {
        "name": req.json().get('filename'),
        "filename": req.json().get('filename'),
        "blob_id": None,
        "asset_id": req.json().get('file_id')
    }
    
    attachments = revision.attributes['attachments']
    attachments.append(file_info)
    return revision.update({
        'attachments': attachments
    })

def upload_state_report(dataset_id, state, domain, socrata_py_client, sodapy_client, SOCRATA_ID, SOCRATA_PASS):
    
    import requests
    import os
    import json
    from datetime import date, timedelta
    import re

    meta_url = f"https://{domain}/api/views/metadata/v1/{dataset_id}"

    view = socrata_py_client.views.lookup(dataset_id)

    revision = view.revisions.create_replace_revision()

    current_date = (date.today() - timedelta(5)).strftime("%Y%m%d")

    filepath = f'input/{state}_State_Profile_Report_{current_date}_Public.pdf' 

    filename = f'{state}_State_Profile_Report_{current_date}_Public.pdf'

    with open(filepath, 'rb') as f:
        files = (
            {'file': (filename, f)}
        )
        response = sodapy_client.replace_non_data_file(dataset_id, {}, files)
    
    last_update =  (date.today() - timedelta(5)).strftime("%b %d, %Y")
    payload = {"customFields": {"Common Core": {"Last Update" : last_update}}}
    json_data = json.dumps(payload)
    req_update = requests.patch(meta_url, json_data, auth=(SOCRATA_ID, SOCRATA_PASS))
    meta_new = req_update.text

    
    revision = view.revisions.create_replace_revision()

    attachment_update = add_attachment(revision, filepath, filename) 
    job = attachment_update.apply()
    job.wait_for_finish(progress=lambda job: print(state, 'attachment upload: ', job.attributes['status']))   

############################################################################
# Define function to approve an asset in the approvals queue

def auto_approve(domain, fxf, state, user_id, user_pw):
    import os
    import requests
    import json

    rev = requests.get(url = f"https://{domain}/api/publishing/v1/revision/{fxf}", auth = (user_id, user_pw))
    if rev.status_code != 200:
        return rev.content
  
    rev_seq = str(json.loads(rev.content)[0]['resource']['revision_seq'])
    qu = requests.get(url = f"https://{domain}/views/{fxf}/approvals?method=guidance&assetId={fxf}:{rev_seq}",  auth = (user_id, user_pw))
    if qu.status_code != 200:
        return qu.content
    if json.loads(qu.content)['currentState'] != "pending":
        return {"Warning": f"No draft waiting for approval; no action taken for {state} SPR"}
  
    updateURL = json.loads(qu.content)['updateUrl']
    approval = requests.put(
        url = f"https://{domain}{updateURL}", json = {"state": "approved"}, auth = (user_id, user_pw))
    if approval.status_code != 200:
        return f"{state} SPR Warning: " + approval.content['Warning']
    else:
        print(f"Success: {state} State Profile Report approved", flush=True)
        return json.loads(approval.content)
