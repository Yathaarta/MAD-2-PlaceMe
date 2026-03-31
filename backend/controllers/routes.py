from flask import Flask, jsonify, request
from app import app, db, user_datastore
from models.dbmodel import *
from flask_security.decorators import auth_required
from flask_login import current_user
from flask_security.utils import hash_password, verify_password, login_user, logout_user
from flask_security.models import fsqla_v3 as fsqla  
from marshmallow import ValidationError
from models.schema import StudentRegisterSchema, CompanyRegisterSchema, validate_official_name, safe_format_date, get_names_from_ids
from datetime import datetime, timezone, date
from .decorators import email_verification_required

import random
import redis

# IMPORT OUR CELERY TASKS
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


# ==========================================================================================
# PUBLIC & AUTHENTICATION ENDPOINTS
# ==========================================================================================

# Initialize schemas once
student_schema = StudentRegisterSchema()
company_schema = CompanyRegisterSchema()


# ----------------- 1. DROPDOWN DATA APIS -----------------

@app.route('/api/degrees', methods=['GET'])
def get_degrees():
    degrees = Degree.query.all()
    degree_list = [{"id": d.id, "name": d.name} for d in degrees]
    return jsonify(degree_list), 200

@app.route('/api/streams/<int:degree_id>', methods=['GET'])
def get_streams_for_degree(degree_id):
    programs = Program.query.filter_by(degree_id=degree_id).all()
    
    streams_list = []
    for p in programs:
        streams_list.append({
            "id": p.stream.id, 
            "name": p.stream.name, 
            "code": p.stream.code, 
            "program_id": p.id,
            "degree_id": degree_id
        })
        
    return jsonify(streams_list), 200


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
            password=hash_password(valid_data['password']), 
            roles=['student'], 
            active=True, 
            confirmed_at=confirmed_time
        )
        db.session.flush()    
        
        # setting name in profile too
        parts = valid_data['full_name'].split(' ', 1)
        profile = StudentProfile(
            user_id=user.id, 
            first_name=parts[0], 
            last_name=parts[1] if len(parts) > 1 else ""
        )
        db.session.add(profile)
        db.session.flush()
        
        # education: program -> (degree, stream)
        if 'degree' in valid_data and 'stream' in valid_data:
             prog = Program.query.filter_by(degree_id=valid_data['degree'], stream_id=valid_data['stream']).first()
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
        
        # adding name, industry, hrcontact, isapproved in company profile
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


# ----------------- 3. AUTHENTICATION & SESSION APIS -----------------

# LOGIN ROUTE
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = user_datastore.find_user(email=data.get('email'))
    
    if user and verify_password(data.get('password'), user.password):
        if not user.active: 
            return jsonify({"error": "Account disabled or blacklisted by Admin."}), 403
            
        login_user(user) # creates session cookie
        
        # role based access - determine role and name of user.
        role = user.roles[0].name
        name = "User"
        
        if role == 'student' and user.student_profile: 
            name = user.student_profile.full_name
        elif role == 'company' and user.company_profile: 
            name = user.company_profile.name
        elif role == 'admin': 
            name = "Admin"
            
        return jsonify({
            "message": "Logged in successfully", 
            "role": role, 
            "name": name, 
            "uniquifier": user.fs_uniquifier
        }), 200
        
    return jsonify({"error": "Invalid email or password"}), 401


# LOGOUT ROUTE
@app.route('/api/logout', methods=['POST'])
def api_logout():
    # destroying the session cookie on backend on logout
    logout_user() 
    return jsonify({"message": "Successfully logged out"}), 200


# AUTH STATUS
@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    # checking if user is currently logged in
    if current_user.is_authenticated:
        role = current_user.roles[0].name
        name = "User"
        
        if role == 'student' and current_user.student_profile: 
            name = current_user.student_profile.full_name
        elif role == 'company' and current_user.company_profile: 
            name = current_user.company_profile.name
        elif role == 'admin': 
            name = "Admin"
            
        return jsonify({
            "is_authenticated": True, 
            "role": role, 
            "name": name, 
            "uniquifier": current_user.fs_uniquifier
        }), 200
        
    return jsonify({"is_authenticated": False}), 401


# ----------------- 4. PASSWORD RESET ROUTES -----------------

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





# ==========================================================================================
# ADMIN ENDPOINTS
# ==========================================================================================

# ----------------- 1. ADMIN DASHBOARD -----------------

@app.route('/api/admin/dashboard', methods=['GET'])
@auth_required('session')
def admin_dashboard():
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    total_students = StudentProfile.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    
    pending_companies = Company.query.filter_by(is_approved=False).count()
    pending_drives = PlacementDrive.query.filter_by(is_approved=False).count()
    
    app_stats = db.session.query(Application.status, db.func.count(Application.application_id)).group_by(Application.status).all()
    chart_status = {status.name: count for status, count in app_stats}
    
    return jsonify({
        "stats": {
            "total_students": total_students,
            "total_companies": total_companies,
            "total_drives": total_drives,
            "pending_companies": pending_companies,
            "pending_drives": pending_drives
        },
        "charts": {
            "application_status": chart_status
        }
    }), 200


# ----------------- 2. MANAGE COMPANIES -----------------

# GET COMPANIES
@app.route('/api/admin/companies', methods=['GET'])
@auth_required('session')
def admin_get_companies():
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    companies = Company.query.all()
    companies_data = []
    
    for c in companies:
        is_complete = bool(c.website and c.description and c.industry and c.hr_contact)
        companies_data.append({
            "id": c.company_id, 
            "name": c.name, 
            "industry": c.industry, 
            "hr_contact": c.hr_contact, 
            "is_approved": c.is_approved, 
            "is_active": c.user.active, 
            "user_id": c.user_id,
            "description": c.description,
            "website": c.website,
            "is_profile_complete": is_complete
        })
        
    return jsonify(companies_data), 200

# APPROVE COMPANY
@app.route('/api/admin/companies/<int:company_id>/approve', methods=['PUT'])
@auth_required('session')
def admin_approve_company(company_id):
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = Company.query.get_or_404(company_id)
    
    # check if required fields are present
    if not company.website or not company.description or not company.industry:
        return jsonify({"error": "Cannot approve. Company has missing required profile fields."}), 400
        
    company.is_approved = True
    db.session.commit()
    
    return jsonify({"message": "Company approved successfully!"}), 200

# TOGGLE BLACKLIST
@app.route('/api/admin/users/<int:user_id>/blacklist', methods=['PUT'])
@auth_required('session')
def admin_toggle_blacklist(user_id):
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    user = User.query.get_or_404(user_id)
    user.active = not user.active
    db.session.commit()
    
    status = 'restored' if user.active else 'blacklisted'
    return jsonify({"message": f"User account has been {status}."}), 200


# ----------------- 3. MANAGE STUDENTS -----------------

# GET STUDENTS
@app.route('/api/admin/students', methods=['GET'])
@auth_required('session')
def admin_get_students():
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    students = StudentProfile.query.all()
    students_data = []
    
    for s in students:
        edu = s.educations[0] if s.educations else None
        prog = Program.query.get(edu.program_id) if edu and edu.program_id else None
        
        cgpa_val = float(edu.cgpa) if edu and edu.cgpa else None
        is_complete = bool(s.age and s.resume_url and cgpa_val and edu.start_year and edu.end_year)
        
        students_data.append({
            "id": s.student_id, 
            "name": s.full_name, 
            "email": s.user.email, 
            "degree": prog.degree.name if prog else "N/A", 
            "stream": prog.stream.name if prog else "N/A", 
            "cgpa": cgpa_val, 
            "verified_edu": edu.verified_edu if edu else False, 
            "is_active": s.user.active, 
            "user_id": s.user_id,
            "is_profile_complete": is_complete
        })
        
    return jsonify(students_data), 200

# VERIFY STUDENT
@app.route('/api/admin/students/<int:student_id>/verify', methods=['PUT'])
@auth_required('session')
def admin_verify_student(student_id):
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = StudentProfile.query.get_or_404(student_id)
    edu = student.educations[0] if student.educations else None
    
    # check for missing data before verifying
    if not edu or not edu.cgpa or not edu.start_year or not edu.end_year or not student.age or not student.resume_url:
        return jsonify({"error": "Cannot verify. Student has missing personal or academic data."}), 400
        
    edu.verified_edu = True
    db.session.commit()
    
    return jsonify({"message": "Student education verified successfully."}), 200


# ----------------- 4. MANAGE DRIVES -----------------

# GET DRIVES
@app.route('/api/admin/drives', methods=['GET'])
@auth_required('session')
def admin_get_drives():
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    drives = PlacementDrive.query.all()
    drives_data = []
    
    for d in drives:
        drives_data.append({
            "id": d.drive_id, 
            "company": d.company.name, 
            "role": d.job_title, 
            "deadline": safe_format_date(d.deadline), 
            "is_approved": d.is_approved, 
            "is_active": d.is_active,
            "description": d.job_description,
            "min_cgpa": float(d.min_cgpa) if d.min_cgpa else "No Minimum",
            "degree_names": get_names_from_ids(Degree, d.allowed_degrees),
            "stream_names": get_names_from_ids(Stream, d.allowed_streams)
        })
        
    return jsonify(drives_data), 200

# APPROVE DRIVE
@app.route('/api/admin/drives/<int:drive_id>/approve', methods=['PUT'])
@auth_required('session')
def admin_approve_drive(drive_id):
    if not current_user.has_role('admin'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    if drive.deadline < datetime.now().date():
        return jsonify({"error": "Cannot approve a drive with a past deadline."}), 400
        
    drive.is_approved = True
    db.session.commit()
    
    return jsonify({"message": "Placement drive approved for students."}), 200