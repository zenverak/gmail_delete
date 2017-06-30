# gmail_delete

This is a simple program that will delete all emails that meet a certain criteria from your gmail account.


### running the program
To run the program you need to edit query in

    if __name__ == '__main__':
        query = ''
        main(query)
    
and then run from idle. ( I could not make it work from command line becaues it kept saying that httplib2 could not be found.

### Getting started with Google API

To prepare for this you will want to go to https://developers.google.com/gmail/api/quickstart/python . It will help you get started on understanding how to use google api. Make sure you name the CLIENT_SECRET_FILE client_secret.json and that it is placed in the same directory as gmail_delete. 

# Queries

More help on gmail queries can be found at https://support.google.com/mail/answer/7190?hl=en


