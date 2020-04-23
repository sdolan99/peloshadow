from __future__ import print_function
import pickle
import os.path
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = ''

class Sheets(object):
  '''Get data from google sheets.  See https://developers.google.com/sheets/api/quickstart/python for more details'''
  def __init__(self, args):
    self.args = args
    self.creds = None
    self.service = None
    
  def login(self, user, password, creds=None):
    # Check the local login tokens if none provided
    if os.path.exists('token.pickle') and creds is None:
      with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
        logging.debug('Loaded credentials from token.pickle')
    if creds is None or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        logging.debug('Credentials have expired. Refreshing')
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
      with open('token.pickle', 'wb') as token:
        logging.debug('Saving credential tokens to token.pickle file')
        pickle.dump(creds, token)
        
    self.service = build('sheets', 'v4', credentials=creds)
    logging.info('Login Succeeded')
    
  def sheet_values(self, cell_range, spreadsheet_id, service=None):
    if self.service is None:
      logging.error('Cannot connect to Sheets. Please log in first')
      return []
    sheet = self.service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=cell_range).execute()
    values = result.get('values', [])
    if not values:
      logging.warn('No values found')
      values = []
    return values