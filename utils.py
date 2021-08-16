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

def upload_state_report(dataset_id, state, domain, auth):
    
    from socrata import Socrata
    import requests
    import os
    import json
    from datetime import date
    import re

    meta_url = f"https://{domain}/api/views/metadata/v1/{dataset_id}"

    socrata = Socrata(auth)

    view = socrata.views.lookup(dataset_id)

    revision = view.revisions.create_replace_revision()

    current_date = date.today().strftime("%Y%m%d")

    filepath = f'input/{state}_State_Profile_Report_{current_date}_Public.pdf' 

    filename = f'{state}_State_Profile_Report_{current_date}_Public.pdf'

    with open(filepath, 'rb') as file:
        upload = revision.source_as_blob(filename)
        source = upload.blob(file)
        job = revision.apply()
        job.wait_for_finish(progress=lambda job: print(state, 'file upload: ', job.attributes['status']))

    revision = view.revisions.create_replace_revision()

    attachment_update = add_attachment(revision, filepath, filename) 
    job = attachment_update.apply()
    job.wait_for_finish(progress=lambda job: print(state, 'attachment upload: ', job.attributes['status']))   

    last_update = date.today().strftime("%b %d, %Y")
    payload = {"customFields": {"Common Core": {"Last Update" : last_update}}}
    json_data = json.dumps(payload)
    req_update = requests.patch(meta_url, json_data, auth=(os.environ['SOCRATA_ID'],os.environ['SOCRATA_KEY']))
    meta_new = req_update.text
