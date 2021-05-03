import os

customhost = os.environ.get('host') or "employee.cprja5yjwh3o.us-east-1.rds.amazonaws.com"
customuser = os.environ.get('databaseuser') or "admin"
custompass = os.environ.get('databaseuserpassword')
customdb = os.environ.get('db') or "employee"
custombucket = os.environ.get('bucketname') or "addemployee07"
customregion = os.environ.get('region') or "us-east-1"
adminusername= os.environ.get('adminpassword') or "admin"
adminpassword= os.environ.get('adminpassword') 