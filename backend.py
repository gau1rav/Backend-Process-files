from flask import Flask, request, jsonify, send_file, Response

import os, zipfile
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)

CURR_DIR = os.getcwd()
ALLOWED_EXTENSIONS = ['xlsx']

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = os.path.join(CURR_DIR, 'uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(CURR_DIR, 'download_folder')

'''
    Method to check if the uploaded filetype is supported by the server
'''

def is_allowed_ext(filename):
    return filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

'''
    Method to check if the query file is previously uploaded by the client

    IF yes then return path ELSE return empty string
'''

def get_path(filename, folder):
    if filename in os.listdir(folder):
        return os.path.join(folder, filename)

    return ""

'''
    Function to roundoff a number to nearest natural number

    IF num < 0.5 THEN num = 1 ELSE round off to nearest integer
'''

def round_to_nearest_n(num):
    return 1 if num < 0.5 else int(round(num))

'''
    Convert the files to be sent to client in a zip form
    This is helpful when server needs to send multiple files together
'''

def make_zip(fileList):
    zipf = zipfile.ZipFile('result.zip','w', zipfile.ZIP_DEFLATED)

    for file in fileList:
        zipf.write(os.path.join(app.config['DOWNLOAD_FOLDER'], file))

    zipf.close()

    return send_file('result.zip',
                    mimetype = 'zip',
                    attachment_filename = 'result.zip',
                    as_attachment = True)

'''
    API to upload the user file

    This API call expects a request header: {'id':<user_id>}

    The above header along with the filename is utilized to create a unique filename for the uploaded file
    This unique name is later used to locate the query file when api calls for task1, task2 and task3 are made
'''

@app.route('/upload', methods = ['POST'])
def file_upload():

    if request.method == 'POST':
        if (request.files):

            upload_file = request.files['file']
            filename = upload_file.filename

            if(not is_allowed_ext(filename)):
                return Response("Invalid extension found", 422)

        unique_filename = request.headers.get('id') + "_" + filename # Create a unique name for this file before saving it on server -- helpful in identifying this file during a query.

        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        return Response("Upload completed successfully", 200)

    return Response("Unable to upload file. Please try again", 400)

'''
    API to filter original file into 3 child files based on CompoundID

    This API call expects request header: {'id':<user_id>, 'filename':<name_of_query_file>}

    Note:

    While converting children dataframes to download files, we use original filename instead of unique identifier for the files.
    This is done to keep user_id of the clients hidden from them -- prevents security breaches
'''

@app.route('/filter_compoundID')
def filter_compoundID():
    filename = request.headers.get('id') + "_" + request.headers.get('filename')

    filepath = get_path(filename, app.config['UPLOAD_FOLDER'])

    if filepath == "":
        return Response("File is not present in server. Please upload your file first", 422)

    print('Processing your file')

    df = pd.read_excel(filepath)

    if 'Accepted Compound ID' not in df:
        return Response("Column Accepted Compound ID does not exist in your file", 400)

    PC_df = df[df['Accepted Compound ID'].str.contains('.*[_ ]PC$', na = False)]
    LPC_df = df[df['Accepted Compound ID'].str.contains('.*[_ ]LPC$', na = False)]
    plasmalogen_df = df[df['Accepted Compound ID'].str.contains(".*[_ ]plasmalogen$", na = False)]

    PC_df.to_excel(os.path.join(app.config['DOWNLOAD_FOLDER'], "PC_" + filename), index = False)
    LPC_df.to_excel(os.path.join(app.config['DOWNLOAD_FOLDER'], "LPC_" + filename), index = False)
    plasmalogen_df.to_excel(os.path.join(app.config['DOWNLOAD_FOLDER'], "plasmalogen_" + filename), index = False)

    return make_zip(["PC_" + filename, "LPC_" + filename, "plasmalogen_" + filename])

'''
'''

@app.route('/roundoff_retention')
def roundoff_retention():
    filename = request.headers.get('id') + "_" + request.headers.get('filename')

    filepath = get_path(filename, app.config['UPLOAD_FOLDER'])

    if filepath == "":
        return Response("Query file not found in server", 422)

    print('Processing your file')

    df = pd.read_excel(filepath)

    if 'Retention time (min)' not in df:
        return Response("Column Retention Time does not exist in file", 400)

    df['Retention Time Roundoff (min)'] = df['Retention time (min)'].apply(round_to_nearest_n)

    df.to_excel(os.path.join(app.config['DOWNLOAD_FOLDER'], "Roundoff_Retention_" + filename), index = False)

    return make_zip(["Roundoff_Retention_" + filename])

@app.route('/find_mean')
def find_mean():
    filename = request.headers.get('id') + "_" + request.headers.get('filename')

    filepath = get_path(filename, app.config['UPLOAD_FOLDER'])

    if filepath == "":
        return Response("Query file not found in server", 422)

    path = get_path('Roundoff_Retention_' + filename, app.config['DOWNLOAD_FOLDER'])

    if path == "":
        return Response("Complete the second task first", 432)

    print('Processing your file')

    df = pd.read_excel(path)
    unique_retention_time = df['Retention Time Roundoff (min)'].unique()

    metabolite_data = df.drop(['m/z', 'Retention time (min)', 'Accepted Compound ID'], axis = 1)
    mean_df = pd.DataFrame(columns = metabolite_data.columns)

    index = 0
    for val in unique_retention_time:
        row = metabolite_data[metabolite_data['Retention Time Roundoff (min)'] == val].mean(axis = 0)
        mean_df.loc[index] = row;
        index += 1

    mean_df.to_excel(os.path.join(app.config['DOWNLOAD_FOLDER'], 'mean_dataFrame_' + filename), index = False)

    return make_zip(['mean_dataFrame_' + filename])

if __name__ == "__main__":

    # If upload and download folders don't exist then create new
    if (not os.path.isdir(app.config['UPLOAD_FOLDER'])):
        os.mkdir(app.config['UPLOAD_FOLDER'])

    if (not os.path.isdir(app.config['DOWNLOAD_FOLDER'])):
        os.mkdir(app.config['DOWNLOAD_FOLDER'])



    app.run(debug = True, port = 5000)
