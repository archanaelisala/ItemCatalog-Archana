# Udacity-FullStackNanodegree Item Catalog Project
Item Catalog Project is a complete RESTfull web application made using Flask framework. It utilizes different features including Authentication & Authorization using OAuth with Google's API, SQLAlchemy for the database operations, JSON endpoints, local permission system, and finally allows registered users to perform Create, Read, Update, and Delete operations.

## Installation
- Download and install [Vagrant](https://www.vagrantup.com/downloads.html).
- Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
- Download [FSND Virtual Machine](https://github.com/udacity/fullstack-nanodegree-vm).

## Google Client ID and Client Secret:

  1. Go to the [Google APIs Console](https://console.developers.google.com/apis)
    
  2. Sign in to your Google account. If you don't have a Google account, you will have to sign up for one.
    
  3. In the sidebar, click Credentials.
    
  4. Click 'Create credentials' and choose 'OAuth Client Id' and then select web application for application type.
    
  5. Give the web application a name. 

  6. For Authorized JavaScript origins add `http://localhost:5000` and For Authorized redirect URIs add 
     `http://localhost:5000/login` && `http://localhost:5000/gconnect` and Select Create.
     
  7. Copy the Client ID and paste it into the `data-clientid` in login.html
    
  8. Download the JSON file and save it as `Gclient_secret.json` and place it in the project directory.


## How to Run
Once you get the above softwares installed and the needed data downloaded:
1. Navigate to your **FSND Virtual Machine** folder and run the following commands:

`vagrant up` - Launch the Vagrant Virtual Machine
`vagrant ssh` - Log into Vagrant Virtual Machine
`cd /vagrant` - To navigate to the shared repository.

2. You need to setup the database using **database_setup.py** by running the following command: 
   `python database_setup.py`

3. After that, run the **populated_db.py** by running the following command: 
   `python populated_db.py`

4. Then, run the server by using the following command: 
   `python catalog.py`

5. Go to your browser, and visit `http://localhost:5000`


## JSON Endpoints
- /catalog/JSON: retrieve a list of all the categories and their items.
- /catalog/<string:category_name>/JSON: retrieve a list of all the items in the specified category.
- /catalog/<string:category>/<int:item_id>/JSON: retrieve item's details.


## Contents
This application is made up of several files, most being templates:
- `catalog.py` Web server, template rendering, and routing is all done here.
- `database_setup.py` Database schema defined here, and will create `itamcatalog.db`.
- `Gclient_secret.json` Provides the client ID and client secret from Google for use with OAuth.
- `templates/` Contains all HTML templates. Each file's name should be self-explanatory.
- `static/` Contains the single style file: `styles.css`.


