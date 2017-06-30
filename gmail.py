import os
import sys
import imp

from httplib2 import Http


from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    #parser.add_argument('-q', type=str, help='a query for emails')

except ImportError:
    flags = None


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gmail-delete'

def get_credentials():
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
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def build_service():
    '''
    This function simply builds the service
    '''
    credentials = get_credentials()
    http =  credentials.authorize(Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service


def prep_messages_for_delete(raw_messages):
    '''
    https://github.com/qualman/gmail_delete_by_filter/blob/master/deleter.py
    Want to thank qualman for figuring out how to format the messages. Everything
    else is something I wrote or gathered from google tutorials. I also extended this
    function to account for the fact that batchDelete can only do 1000 at a time.

    Arguments:
      raw_messages - The messages in a raw format.

    Returns:
      emails - A list of lists. Each element list contains at most 1000 records
    '''
    emails = []
    not_empty = True
    while not_empty:
        r_len = len(raw_messages)
        if r_len > 1000:
            partial_raw = raw_messages[0:1000]
            raw_messages = raw_messages[1000::]
        else:
            partial_raw = raw_messages[0:r_len]
            not_empty = False
        message = {'ids': []}
        message['ids'].extend([str(d['id']) for d in partial_raw])
        emails.append(message)

        print("got {0} ids".format(len(message['ids'])))
    return emails


def get_emails(text, service):
    '''
       This function takes in the text, where text is the query, and then applies
       it to gather all of the emails that meet said query.

       Arguments
           text - Query. It can be any gmail filter applied in your inbox on the web.
           service - return from build_service()

        returns:
            All emails that meet the query requirement
    '''
    try:
        response = service.users().messages().list(userId='me', q=text).execute()
        print "response {0}".format(response)
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token =  response['nextPageToken']
            response = service.users().messages().list(userId='me',q=text,pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except errors.HttpError, error:
        print "we gots errors {0}".format(error)
        pass
    pass


def batch_delete(service, emails):
    '''
    This will batch delete all emails contains in emails

    Arguments:
        Service - service returned from build_service()
        emails - emails needs to be a list of properly formatted messages
                with at most 1000 emails
        
    '''
    try:
        service.users().messages().batchDelete(userId='me', body=emails).execute()
    except errors.HttpError, error:
        print error


def main(query):
        if query == '':
            print "Please provide a query"
        else:
            
            service = build_service()
            emails = get_emails(query, service)
            emails = prep_messages_for_delete(emails)

        ##    print len(emails)
            for email_set in emails:
                batch_delete(service, email_set)
        
    


if __name__ == '__main__':
    query = ''
    main(query)
