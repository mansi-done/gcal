import requests
import json
from django.shortcuts import redirect
from django.http import HttpResponse

'''
Check https://developers.google.com/identity/protocols/oauth2/web-server#httprest_2 for more information 
on using OAuth2 for Authorization to access Google APIs.
'''

''' ------ Global  ------ '''
# Reading the client.json file which contains the client information.
with open("client.json") as jsonFileClient:
                clientJSON = json.load(jsonFileClient)
                jsonFileClient.close()

# Reading the api_key.json file which contains the API KEY.
with open("api_key.json") as jsonFileApiKey:
                apiJSON = json.load(jsonFileApiKey)
                jsonFileApiKey.close()

# API KEY to access the Google Calendar API's.
API_KEY = apiJSON['api_key'];

# The url where the google oauth should redirect after a successful login.
REDIRECT_URI = 'http://localhost:8000/rest/v1/calendar/redirect/'

# Authorization Scope:Here we only use one which can enable us to view and edit the event.
SCOPE = 'https://www.googleapis.com/auth/calendar'

''' ---- ---- ---- ---- '''


'''
View Name : GoogleCalendarInitView
Paramaters : request
Path: "rest/v1/calendar/init/"

This view redirect the user to Google's OAuth 2.0 server to initiate
the authentication and authorization process.

Google's OAuth 2.0 server authenticates the user and obtains consent 
from the user for the application to access the requested scopes and
redirects back to the application.
'''
def GoogleCalendarInitView(request):
    # Base URL
    url = 'https://accounts.google.com/o/oauth2/v2/auth'

    # URL parameters
    client_id = clientJSON['web']['client_id'];
    access_type = "online"
    include_granted_scopes="true"
    response_type = "code"
    state="there"

    # Complete URL that needs to be redirected to
    URL = url+"?scope="+SCOPE+"&access_type="+access_type+"&include_granted_scopes="+include_granted_scopes+"&response_type="+response_type+"&state="+state+"&redirect_uri="+REDIRECT_URI+"&client_id="+client_id
    return redirect(URL)



'''
View Name : GoogleCalendarRedirectView
Parameters: request
Path: "rest/v1/calendar/redirect/"

This view recives the authorization code from Google API and exchanges it
for access token, then uses the access token to access the list of events
in the calendar.

*If there is error parameter present in the Query Param Dictionary then
the error is returned as a response
'''
def GoogleCalendarRedirectView(request):
        res = request.GET

        # If any error is returned
        if 'error' in res:
                return HttpResponse(request.GET['error'])

        # Fetching the authorization code from the response of Google OAuth Server
        authorization_code = request.GET['code']      

        # Parameters required to be sent to the server
        url = 'https://oauth2.googleapis.com/token';
        client_id = clientJSON['web']['client_id']
        client_secret = clientJSON['web']['client_secret']
        data = {"code": authorization_code, "client_id":client_id,"client_secret":client_secret,"grant_type":"authorization_code","redirect_uri":REDIRECT_URI}

        # Fetching access token in exchange of the authorization code
        response = requests.post(url,data=data)
        tokenJSON = response.json();
        ACCESS_TOKEN = tokenJSON['access_token'];

        calendar_id = "primary"

        # Base URL to fetch list of events of user
        event_url = "https://www.googleapis.com/calendar/v3/calendars/"+calendar_id+"/events"

        # Calendar params and headers to be sent with the request
        params = dict()
        params['key'] = API_KEY
        headers = {'Authorization': "Bearer "+ACCESS_TOKEN , 'Accept': 'application/json'}

        # Making request for the list of events
        events = requests.get(event_url,params=params,headers=headers)

        return HttpResponse(events, content_type="application/json")


'''
Home Page
'''
def HomePage(request):
        homepagestring = "Back End Assignment for Convin AI (Submitted by Mansi Saini)"
        return HttpResponse(homepagestring)

