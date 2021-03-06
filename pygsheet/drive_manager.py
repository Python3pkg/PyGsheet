# -*- coding: utf-8 -*-

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

class DriveManager():
    def __init__(self, secret_file='client_secret.json', app_name='Drive API Python Quickstart'):
        self.secret_file = secret_file
        self.app_name = app_name
        self.service = self.get_service()
    
    
    def get_credentials(self):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'python-quickstart.json')
    
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.secret_file, scope=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
            flow.user_agent = self.app_name
            try:
                import argparse
                flags = argparse.ArgumentParser(parents=[tools.argparser], conflict_handler='resolve').parse_args()
            except ImportError:
                flags = None
            try:
                credentials = tools.run_flow(flow, store, flags)
            except: # Needed only for compatibility with Python 2.6
                try:
                    credentials = tools.run_flow(flow, store)
                except:
                    credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials
    
    def get_service(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build('drive', 'v3', http=http)
    
    def share_file(self, file_id, domain=None, user_list=None):
        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print(exception)
            else:
                print("Permission Id: %s" % response.get('id'))
        
        batch = self.service.new_batch_http_request(callback=callback)
        
        if user_list:
            for email in user_list:
                batch.add(self.service.permissions().create(
                    fileId=file_id,
                    body= {'type': 'user', 'role': 'writer', 'emailAddress': email},
                    fields='id',
                ))
            if domain:
                batch.add(self.service.permissions().create(
                    fileId=file_id,
                    body={'type': 'domain', 'role': 'commenter', 'domain': domain},
                    fields='id',
                ))
        
        batch.execute()
        
    def update_sharing(self):
        pass
    
    def move_file_to_folder(self, file_id, folder_id, remove_parents=False, team_drives=True):
        
        if remove_parents:
            file = self.service.files().get(fileId=file_id,
                                         fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            file = self.service.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            removeParents=previous_parents,
                                            fields='id, parents',
                                            supportsTeamDrives=team_drives).execute()
        else:
            self.service.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            fields='id, parents',
                                            supportsTeamDrives=team_drives).execute()
        
