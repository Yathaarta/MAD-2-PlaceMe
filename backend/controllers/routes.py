from flask import Flask, jsonify, request
from app import app, db, user_datastore
from models.dbmodel import *
from flask_security.decorators import auth_required
from flask_security.utils import hash_password, verify_password, login_user, logout_user
from flask_security.models import fsqla_v3 as fsqla  
from marshmallow import ValidationError
from models.schema import StudentRegisterSchema, CompanyRegisterSchema
from datetime import datetime, timezone

import random
import redis
from tasks import send_otp_email

# ---------------------- INITIALIZE REDIS CLIENT ----------------------

redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

# ---------------------- UNIVERSAL ERROR HANDLERS ----------------------

@app.errorhandler(404)
def resource_not_found(e):
    
    # universally handling any requests on wrong/undefined endpoints
    return jsonify({"error": "Endpoint not found", "status": 404}), 404


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(e):

    # e.messages contains the specific errors from the marshmellow schema
    return jsonify({"errors": e.messages, "status": 400}), 400


@app.errorhandler(500)
def internal_server_error(e):

    # To catches unexpected errors.
    return jsonify({"error": "Internal Server Error", "status": 500}), 500


# ================================================= ROUTES ================================================= /

# Initialize schema once
student_schema = StudentRegisterSchema()
company_schema = CompanyRegisterSchema()

# ----------------- 1. DROPDOWN DATA APIS -----------------

@app.route('/api/degrees', methods=['GET'])
def get_degrees():
    degrees = Degree.query.all()
    return jsonify([
        {"id": d.id, "name": d.name} for d in degrees
    ])

@app.route('/api/streams/<int:degree_id>', methods=['GET'])
def get_streams_for_degree(degree_id):
    programs = Program.query.filter_by(degree_id=degree_id).all()
    
    streams_list = []
    for prog in programs:
        streams_list.append({
            "id": prog.stream.id,
            "name": prog.stream.name,
            "code": prog.stream.code,
            "program_id": prog.id 
        })
        
    return jsonify(streams_list)


# ----------------- 2. REGISTRATION API -----------------

# REGISTER_STUDENT
@app.route('/api/register/student', methods=['POST'])
def register_student():

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    valid_data = student_schema.load(json_data)

    # checking duplicates
    if user_datastore.find_user(email=valid_data['email']):
        return jsonify({"error": "Email already registered."}), 409
    
    # --- opt verification  ---
    confirmed_time = None
    if redis_client.get(f"verified_email:{valid_data['email']}") == "true":
        confirmed_time = datetime.now(timezone.utc)
        redis_client.delete(f"verified_email:{valid_data['email']}")


    try:
        # creating user for student
        user = user_datastore.create_user(
            email=valid_data['email'],
            password= hash_password(valid_data['password']), 
            roles=['student'],
            active=True,
            confirmed_at=confirmed_time
        )
        db.session.flush()    

        # setting name in profile too
        full_name = valid_data['full_name']
        parts = full_name.split(' ', 1)
        fname = parts[0]
        lname = parts[1] if len(parts) > 1 else ""

        profile = StudentProfile(
            user_id=user.id,                     
            first_name=fname,       
            last_name=lname,       
        )
        
        db.session.add(profile)
        db.session.flush()

        # education: program -> (degree, stream)
        if 'degree' in valid_data and 'stream' in valid_data:
             
             prog = Program.query.filter_by(
                 degree_id=valid_data['degree'], 
                 stream_id=valid_data['stream']
             ).first()
             
             if prog:
                 edu = Education(student_id=profile.student_id, program_id=prog.id)
                 db.session.add(edu)

        db.session.commit()
        return jsonify({"message": "Student registered successfully", "email": user.email}), 201

    except Exception as e:
        db.session.rollback() 
        print(f"Registration Error: {e}")
        return jsonify({"error": "System error during registration"}), 500
    

# REGISTER_COMPANY
@app.route('/api/register/company', methods=['POST'])
def register_company():

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    valid_data = company_schema.load(json_data)
    
    if user_datastore.find_user(email=valid_data['hr_email']):
        return jsonify({"error": "Email already registered."}), 409

    # --- otp verification ---
    confirmed_time = None
    if redis_client.get(f"verified_email:{valid_data['hr_email']}") == "true":
        confirmed_time = datetime.now(timezone.utc)
        redis_client.delete(f"verified_email:{valid_data['hr_email']}")
    

    try:
        # creating user
        user = user_datastore.create_user(
            email=valid_data['hr_email'],
            password=hash_password(valid_data['password']),
            roles=['company'],
            active=True,
            confirmed_at=confirmed_time
        )
        db.session.flush() 

        # adding name,industy,hrcontact,isapproved in company profile
        company = Company(
            user_id=user.id,
            name=valid_data['company_name'],
            industry=valid_data['industry'],
            hr_contact=valid_data['hr_email'],
            is_approved=False 
        )
        db.session.add(company)
        
       
        db.session.commit()
        return jsonify({"message": "Registration successful! Pending Admin approval.", "email": user.email}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Company Reg Error: {e}")
        return jsonify({"error": "System error during registration"}), 500
    

# SENDING_OTP'S
@app.route('/api/send-registration-otp', methods=['POST'])
def send_registration_otp():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Please enter an email first."}), 400
        
    if user_datastore.find_user(email=email):
        return jsonify({"error": "Email already registered."}), 409

    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"reg_otp:{email}", 600, otp) # 10 min expiry
    
    send_otp_email.delay(email, otp)
    return jsonify({"message": "OTP sent! Check your inbox."}), 200


# VERIFYING_OTP'S
@app.route('/api/verify-registration-otp', methods=['POST'])
def verify_registration_otp():
    data = request.get_json()
    email = data.get('email')
    submitted_otp = data.get('otp')

    cached_otp = redis_client.get(f"reg_otp:{email}")
    if not cached_otp or cached_otp != submitted_otp:
        return jsonify({"error": "Invalid or expired OTP."}), 400

    # if otp is correct
    redis_client.delete(f"reg_otp:{email}")
    redis_client.setex(f"verified_email:{email}", 600, "true")
    return jsonify({"message": "Email verified successfully!"}), 200


# ----------------- LOGIN ROUTE -----------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = user_datastore.find_user(email=data.get('email'))
    
    if user and verify_password(data.get('password'), user.password):
        if not user.active:
            return jsonify({"error": "Account disabled pending admin approval."}), 403
            
        login_user(user)    # creates session cookie
        
        # role based access - determine role of user.
        role = user.roles[0].name if user.roles else "student"
        return jsonify({"message": "Logged in successfully", "role": role}), 200
        
    return jsonify({"error": "Invalid email or password"}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    # destroying the session cookie on backend on logout
    logout_user() 
    return jsonify({"message": "Successfully logged out"}), 200


# ----------------- PASSWORD RESET ROUTES -----------------

# SENDING_PASSWD_CHANGE_REQ_OTP
@app.route('/api/reset-password/request', methods=['POST'])
def request_password_reset():
    email = request.json.get('email')
    user = user_datastore.find_user(email=email)
    
    if not user:
        return jsonify({"error": "No account found with that email."}), 404

    # if test user i.e unverified email, change passwd directly
    if not user.confirmed_at:
        return jsonify({"message": "Unverified account. Proceed to reset directly.", "requires_otp": False}), 200

    # if verified user, change via otp auth.
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"reset_otp:{email}", 600, otp) # 10 mins
    
    # Send email via celery task
    send_otp_email.delay(email, otp)
    
    return jsonify({"message": "OTP sent to your registered email.", "requires_otp": True}), 200

# VERIFYING_OTP
@app.route('/api/reset-password/confirm', methods=['POST'])
def confirm_password_reset():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')
    otp_submitted = data.get('otp')

    user = user_datastore.find_user(email=email)
    if not user:
        return jsonify({"error": "Invalid request"}), 400

    if user.confirmed_at:
        cached_otp = redis_client.get(f"reset_otp:{email}")
        if not cached_otp or cached_otp != otp_submitted:
            return jsonify({"error": "Invalid or expired OTP."}), 400
        
        # if otp is correct
        redis_client.delete(f"reset_otp:{email}")

    # change passwd in db
    user.password = hash_password(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password successfully reset!"}), 200