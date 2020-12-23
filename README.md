# Backend-Process-files
Flask server for Process files web app which allows clients to upload files and perform several queries(tasks) on them. The server is configured to run on port 5000.
Refer to the image attached for a visual represntation of the running server:

![Frontend](backend.png)

## Steps to run the server

###### Clone the repo
`git clone https://github.com/gau1rav/Backend-Process-files`

###### Create a new virtual environment (Optional but Recommended)
Following commands can be used to create a new virtual environment using python3

`python3 -m pip install --user virtualenv`\
`python3 -m venv <env_name>`

Activate the virtual environment and go to the directory where the repo is cloned

###### Install dependencies
`pip install -r requirements.txt`

###### Start server
`python3 backend.py`

## End points

1. Post request on `http://localhost:5000/upload` to upload a file on the server.
2. Get request on `http://localhost:5000/filter_compoundID` to split the uploaded file into 3 child files (based upon if the Accepted CompoundID ends with PC, LPC or plasmalogen).
3. Get request on `http://localhost:5000/roundoff_retention` to roundoff the retention time to nearest natural number
4. Get request on `http://localhost:5000/find_mean` to find the mean of all the metabolites which have same "Retention Time Roundoff" across all the samples.

**Note: Server will return a zip file contanining the result in excel sheets for GET requests*


## Learn more
Learn more about virtual environments from [Virtual env documentation](https://docs.python.org/3.9/library/venv.html).
