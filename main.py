import hashlib
from flask import Flask, request, jsonify, session
from flask_mysqldb import MySQL
import datetime
import logging
import socket
import MySQLdb.cursors
import jwt
from functools import wraps

app = Flask(__name__)

app.secret_key = 'Meghana'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'meghana'
app.config['MYSQL_DB'] = 'clinicalfirst'

mysql = MySQL(app)

# logging.basicConfig(filename="C://Users//kotid//my logging//text.log",
#                      level=logging.DEBUG,
#                      format="%(levelname)s %(asctime)s - %(message)s")

def get_ip():
    host_name = socket.gethostname()
    ipaddr = socket.gethostbyname(host_name)
    return ipaddr

def get_device():
    host_name = socket.gethostname()
    return host_name

def get_date():
    date = datetime.datetime.now()
    return date

def wrap(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401
        return f(*args, **kwargs)

    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            logger = logging.getLogger()
            user_signup = request.json
            user_mail_id = user_signup.get('USER_MAIL_ID')
            user_password = user_signup.get('USER_PASSWORD')
            PASSWORD= hashlib.md5(user_password.encode())

            status = 200
            if user_mail_id == '' or user_password == '' or user_mail_id is None or user_password is None:
                status = 400
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("select * from user_signup where USER_MAIL_ID=%s and USER_PASSWORD = % s ",
                        (user_mail_id, PASSWORD.hexdigest()))
            account = cur.fetchone()
            print(account)

            if account is not None:
                user_id = account['USER_ID']
                session['USER_ID'] = account['USER_ID']
                print(session['USER_ID'],'75')
                sql_method(user_id, status)
                logger.info('welcome to trails loggin.')
                token = jwt.encode({'user_id': account['USER_ID']}, "secret", algorithm="HS256")
                return jsonify({'token': token}), 200
            else:
                status = 400
                user_id = 0
                sql_method(user_id, status)
                logger.error("This is for error.")
                return jsonify({'message': 'user not found, register'}), 400

        return jsonify({'message': 'invalid'})
    except Exception as e:
        print(e)
        status = 500
        sql_method(user_id, status)
        return jsonify({'message': 'problem with server'}), 500

def sql_method(user_id,status):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO api_logs (USER_ID,triggered_time,api_requested_remote_url, api_name, api_method, "
                   "error_code, IP_ADDRESS, USER_DEVICE) "
                   "values(%s,%s,%s,%s,%s,%s,%s,%s)",
                   (user_id, get_date(), request.url, request.path, request.method, status, get_ip(), get_device()))
    mysql.connection.commit()
    cursor.close()

def max_id_value(c):
    max_value_query = "SELECT substring(user_id,6) as id FROM user_signup WHERE substring(user_id,6)=(SELECT MAX(" \
                      "CAST(SUBSTRING(user_id,6) AS SIGNED)) FROM user_signup) "
    c.execute(max_value_query)
    result_value = c.fetchone()
    if result_value == 0 or result_value == 'None' or result_value == '' or result_value is None:
        result_value = 1;
        return result_value
    else:
        result_value = int(result_value[0]) + 1
        return result_value

@app.route('/user_department', methods=['POST'])
@wrap
def user_department():
    try:
        if request.method == 'POST' and 'DEPT_NAME' in request.json and 'DEPT_HEAD' in request.json and 'DEPT_ID' in \
                request.json:
            user_department = request.json

            user_id = session['USER_ID']
            dept_id = user_department['DEPT_ID']
            dept_name = user_department['DEPT_NAME']
            dept_head = user_department['DEPT_HEAD']
            user_ip = get_ip()
            user_device = get_device()
            cur = mysql.connection.cursor()
            insert_sql_query = "INSERT INTO user_department  VALUES (null,%s,%s,%s,%s,%s,%s)"
            cur.execute(insert_sql_query, (user_id, dept_id, dept_name, dept_head,user_ip,user_device))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'User Department details entered successfully'}), 200
        else:
            return jsonify({'message': 'User Department  data not inserted'}), 401
    except Exception as e:
        print(e)
    return jsonify({'message': 'Out of User Department'}), 500

@app.route('/user_hospital', methods=['POST'])
@wrap
def user_hospital():
    try:
        if request.method == 'POST' and 'HOSPITAL_NAME' in request.json and 'HOSPITAL_CITY' in request.json and 'HOSPITAL_COUNTRY' in request.json and 'HOSPITAL_ZIP_CODE' in request.json:
            user_hospital_details = request.json
            cur = mysql.connection.cursor()
            user_id = session['USER_ID']
            hospital_name = user_hospital_details['HOSPITAL_NAME']
            hospital_city = user_hospital_details['HOSPITAL_CITY']
            hospital_country = user_hospital_details['HOSPITAL_COUNTRY']
            hospital_zip_code = user_hospital_details['HOSPITAL_ZIP_CODE']
            insert_sql_query = "INSERT INTO user_hospital  VALUES (null,%s,%s,%s,%s,%s)"
            cur.execute(insert_sql_query, (user_id, hospital_name, hospital_city, hospital_country, hospital_zip_code))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'hospital details entered successfully'}), 200
        else:
            return jsonify({'message': 'user_hospital data not inserted'}), 401
    except Exception as e:
        print(e)
    return jsonify({'message': 'Out of user_hospital'}), 500

@app.route('/user_qualification', methods=['POST'])
@wrap
def user_qualification():
    try:
        if request.method == 'POST' and 'USER_QUALIFICATION_NAME' in request.json and 'INSTITUTE_NAME' in request.json \
                and 'PROCUREMENT_YEAR' in request.json:
            user_qualification_details = request.json
            cur = mysql.connection.cursor()
            user_id = session['USER_ID']
            user_qualification_name = user_qualification_details['USER_QUALIFICATION_NAME']
            institute_name = user_qualification_details['INSTITUTE_NAME']
            procurement_year = user_qualification_details['PROCUREMENT_YEAR']
            insert_sql_query = "INSERT INTO user_qualification  VALUES (null,%s,%s,%s,%s)"
            cur.execute(insert_sql_query, (user_id, user_qualification_name, institute_name, procurement_year))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'User Qualification details entered successfully'}), 200
        else:
            return jsonify({'message': 'User Qualification  data not inserted'}), 401
    except Exception as e:
        print(e)
    return jsonify({'message': 'Out of User Qualification'}), 500

@app.route('/user_register', methods=['POST'])
@wrap
def api_register():
    try:
        if request.method == 'POST' and 'USER_AGE' in request.json and 'USER_EXPERIANCE' in request.json and 'USER_GENDER' in request.json and 'USER_LICENSE_NUMBER' in request.json and 'FLAT_NO' in request.json and 'STREET_NAME' in request.json and 'CITY_NAME' in request.json  and 'STATE_NAME' in request.json and 'COUNTRY_NAME' in request.json and 'ZIP_CODE' in request.json and 'USER_IP' in request.json:
            new_registration = request.json
            cur = mysql.connection.cursor()
            user_id = session['USER_ID'];
            user_age = new_registration['USER_AGE']
            user_experiance = new_registration['USER_EXPERIANCE']
            user_gender = new_registration['USER_GENDER']
            user_license_number = new_registration['USER_LICENSE_NUMBER']
            flat_no = new_registration['FLAT_NO']
            street_name = new_registration['STREET_NAME']
            city_name = new_registration['CITY_NAME']
            state_name = new_registration['STATE_NAME']
            country_name = new_registration['COUNTRY_NAME']
            zip_code = new_registration['ZIP_CODE']
            user_approved = get_date()
            user_ip = new_registration['USER_IP']
            user_date_registered = get_date()
            insert_sql_query = "INSERT INTO user_registration  VALUES (null,% s,% s, % s,% s,% s, % s,% s,% s, % s,% s,% s, % s,% s,% s) "
            cur.execute(insert_sql_query, (
                user_id, user_age, user_experiance, user_gender, user_license_number, flat_no, street_name, city_name,
                state_name, country_name, zip_code, user_approved, user_ip, user_date_registered))
            mysql.connection.commit()
            cur.close()
            return 'Student inserted successfully'
        else:
            return 'data not inserted'

    except Exception as e:
        print(e)
    return ' Came out of Register'

@app.route('/user_specialization', methods=['POST'])
@wrap
def user_specialization():
    try:
        if request.method == 'POST' and 'SPECIALIZATION_NAME' in request.json:
            user_qualification_details = request.json
            cur = mysql.connection.cursor()
            user_id = session['USER_ID']
            user_specialization_name = user_qualification_details['SPECIALIZATION_NAME']
            insert_sql_query = "INSERT INTO user_specialization  VALUES (null,%s,%s)"
            cur.execute(insert_sql_query, (user_id, user_specialization_name))
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'User Specialization details entered successfully'}), 200
        else:
            return jsonify({'message': 'User Specialization  data not inserted'}), 401
    except Exception as e:
        print(e)
    return jsonify({'message': 'Out of User Specialization'}), 500






if __name__ == '__main__':
    app.run(debug=True)



