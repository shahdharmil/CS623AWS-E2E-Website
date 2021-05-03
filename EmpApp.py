import io

from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from PIL import Image
import json

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmployee.html')


@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()



    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return render_template('Error1.html')

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('EmployeeAdd_Success.html', name=emp_name)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
   return render_template("admin.html")

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("GetEmployeeInfo.html")

@app.route("/fetchdata", methods=['POST'])
def FetchEmp():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT empid, fname, lname, pri_skill, location from employee where empid=%s"
    cursor = db_conn.cursor()
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    s3 = boto3.resource('s3')

    bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
    s3_location = (bucket_location['LocationConstraint'])

    if s3_location is None:
        s3_location = ''
    else:
        s3_location = '-' + s3_location

    image_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        s3_location,
        custombucket,
        emp_image_file_name_in_s3)

    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()

        output["emp_id"] = result[0]
        print('EVERYTHING IS FINE TILL HERE')
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        print(output["emp_id"])





        return render_template("EmployeeInfo_Output.html", id=output["emp_id"], fname=output["first_name"],
                               lname=output["last_name"], interest=output["primary_skills"], location=output["location"], image_url=image_url)

    except Exception as e:
        print(e)
        return render_template('Error.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
