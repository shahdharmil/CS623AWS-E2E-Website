import io

from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
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

@app.route("/atdsuccess", methods=['GET', 'POST'])
def StuAttend():
    return render_template('attend_success.html')

@app.route("/StudentAttend", methods=['GET', 'POST'])
def StudentAttend():
    return render_template('StudentAttend.html')
    
    print('In POST if')
    output = {}
    select_sql = "SELECT empid, subject_database from employee where empid=%s" 
    cursor = db_conn.cursor()
    
    try:
        print('In POST try')
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()
        
        output["emp_id"] = result[0]
        
        if result[1] is 0 or None:
            print('In POST if cond')
            result[1] = 1
            output["subject_database"] = int(result[1])
        else:
            print('In POST else cond')
            output["subject_database"] = int(result[1]) + 1
        
        
        print(result[5])
        
        update_sql = "UPDATE employee SET subject_database = %s WHERE empid=%s"
        cursor.execute(update_sql, (str(output["subject_database"]), (emp_id)))
        
        db_conn.commit()
        
        return render_template('StudentAttend.html')
        
    except Exception as e:
        print(e)
        return render_template('Error.html')

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/std", methods=['GET', 'POST'])
def std():
    return render_template('std.html')


@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route("/AddEmployee", methods=['GET','POST'])
def AddEmployee():
    return render_template('AddEmployee.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    return render_template('EmployeeAdd_Success.html')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
   return render_template("admin.html")

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("GetEmployeeInfo.html")

@app.route("/fetchdata", methods=['POST'])
def FetchEmp():
    
  if request.method == 'POST':
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT empid, fname, lname, pri_skill, location, subject_database from employee where empid=%s"
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
        output["subject_database"] = result[5]
        print(output["emp_id"])
        return render_template("EmployeeInfo_Output.html", id=output["emp_id"], fname=output["first_name"],
                               lname=output["last_name"], interest=output["primary_skills"], location=output["location"], subject_database=output["subject_database"])

    except Exception as e:
        print(e)
        return render_template('Error.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
