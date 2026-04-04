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
from tasks import send_otp_email, export_company_applicants_csv

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


# ---------------------- Helper Functions ----------------------

def auto_close_expired_drives():
    # Checks the entire database for active drives that have passed their deadline and permanently sets them to inactive.
    today = date.today()
    
    # Efficiently query ONLY drives that are active but expired
    expired_drives = PlacementDrive.query.filter(
        PlacementDrive.is_active == True,
        PlacementDrive.deadline < today
    ).all()
    
    # If it found any, update them and save the database
    if expired_drives:
        for drive in expired_drives:
            drive.is_active = False
        db.session.commit()


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
    
    auto_close_expired_drives()    
    drives = PlacementDrive.query.all()
    drives_data = []
    
    for d in drives:
        drives_data.append({
            "id": d.drive_id, 
            "company": d.company.name, 
            "role": d.job_title, 
            "deadline": safe_format_date(d.deadline), 
            "updated_at": d.updated_at.isoformat() + "Z",
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



# ==========================================================================================
# COMPANY ENDPOINTS
# ==========================================================================================

# ----------------- 1. COMPANY DASHBOARD -----------------

@app.route('/api/dashboard/company', methods=['GET'])
@auth_required('session')
def company_dashboard_data():
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = current_user.company_profile
    drives = PlacementDrive.query.filter_by(company_id=company.company_id).all()
    
    total_drives = len(drives)
    active_drives = sum(1 for d in drives if d.is_active)
    total_applicants = sum(len(d.applications) for d in drives)
    
    recent_drives = sorted(drives, key=lambda x: x.created_at, reverse=True)[:3]
    recent_drives_data = []
    
    chart_drives = {d.job_title: len(d.applications) for d in drives if len(d.applications) > 0}
    
    for d in recent_drives:
        recent_drives_data.append({
            "id": d.drive_id, 
            "role": d.job_title, 
            "deadline": safe_format_date(d.deadline), 
            "updated_at": d.updated_at.isoformat() + "Z",
            "is_active": d.is_active,
            "is_approved": d.is_approved, 
            "applicants": len(d.applications)
        })

    return jsonify({
        "company": {
            "name": company.name, 
            "industry": company.industry, 
            "is_approved": company.is_approved
        },
        "stats": {
            "total_drives": total_drives, 
            "active_drives": active_drives, 
            "total_applicants": total_applicants
        },
        "recent_drives": recent_drives_data,
        "charts": {"applicants_per_drive": chart_drives}
    }), 200


# ----------------- 2. MANAGE DRIVES -----------------

@app.route('/api/company/drives', methods=['GET', 'POST'])
@auth_required('session')
def manage_company_drives():
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = current_user.company_profile

    auto_close_expired_drives()    

    # get all drives
    if request.method == 'GET':
        drives = PlacementDrive.query.filter_by(company_id=company.company_id).order_by(PlacementDrive.created_at.desc()).all()
        
        drives_data = []
        for d in drives:
            drives_data.append({
                "id": d.drive_id, 
                "role": d.job_title, 
                "description": d.job_description,
                "min_cgpa": float(d.min_cgpa) if d.min_cgpa else None, 
                "deadline": safe_format_date(d.deadline), 
                "updated_at": d.updated_at.isoformat() + "Z",
                "is_active": d.is_active, 
                "is_approved": d.is_approved, 
                "applicants": len(d.applications),
                # resolving names for the detailed edit modal
                "degree_names": get_names_from_ids(Degree, d.allowed_degrees),
                "stream_names": get_names_from_ids(Stream, d.allowed_streams)
            })
            
        return jsonify(drives_data), 200

    # create new drive
    if request.method == 'POST':
        if not company.is_approved: 
            return jsonify({"error": "Company not approved by Admin."}), 403
            
        data = request.get_json()
        deadline_date = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        
        # check if deadline is in the past
        if deadline_date < datetime.now().date():
            return jsonify({"error": "Deadline cannot be in the past."}), 400
            
        new_drive = PlacementDrive(
            company_id=company.company_id, 
            job_title=data['job_title'], 
            job_description=data.get('job_description', ''),
            min_cgpa=data.get('min_cgpa'), 
            allowed_degrees=data.get('allowed_degrees', ''), 
            allowed_streams=data.get('allowed_streams', ''),
            deadline=deadline_date, 
            is_active=True, 
            is_approved=False
        )
        db.session.add(new_drive)
        db.session.commit()
        
        return jsonify({"message": "Drive submitted! Pending Admin Approval."}), 201

# UPDATE DRIVE
@app.route('/api/company/drives/<int:drive_id>', methods=['PUT'])
@auth_required('session')
def update_company_drive(drive_id):
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = current_user.company_profile
    auto_close_expired_drives() 
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    if drive.company_id != company.company_id:
        return jsonify({"error": "Unauthorized action."}), 403
    if not drive.is_active:
        return jsonify({"error": "Cannot edit this drive. The deadline has already passed."}), 403
        
    data = request.get_json()
    
    # toggle active status (end drive early)
    if 'is_active' in data:
        drive.is_active = False
        db.session.commit()

        return jsonify({"message": "Drive closed early."}), 200
    
    # update job description
    if 'job_description' in data:
        drive.job_description = data['job_description']
        
    # extend deadline
    if 'deadline' in data:
        new_deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        
        if new_deadline < datetime.now().date():
            return jsonify({"error": "New deadline cannot be in the past."}), 400
            
        drive.deadline = new_deadline
        
    db.session.commit()
    return jsonify({"message": "Drive updated successfully."}), 200


# ----------------- 3. APPLICATIONS & PROFILE -----------------

# GET APPLICATIONS
@app.route('/api/company/applications', methods=['GET'])
@auth_required('session')
def get_company_applications():
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = current_user.company_profile
    apps_data = []
    
    for drive in company.drives:
        for app in drive.applications:
            student = app.student
            edu = student.educations[0] if student.educations else None
            prog = Program.query.get(edu.program_id) if edu and edu.program_id else None
            
            apps_data.append({
                "id": app.application_id, 
                "drive_role": drive.job_title, 
                "student_name": student.full_name, 
                "student_email": student.user.email,
                "resume_url": student.resume_url, 
                "cgpa": float(edu.cgpa) if edu and edu.cgpa else "N/A",
                "degree": prog.degree.name if prog else "N/A", 
                "stream": prog.stream.name if prog else "N/A",
                "status": app.status.value, 
                "applied_on": safe_format_date(app.created_at),
                "is_blacklisted": not student.user.active,
                # extra details for candidate modal
                "age": int(student.age) if student.age else None,
                "start_year": safe_format_date(edu.start_year) if edu else "N/A",
                "end_year": safe_format_date(edu.end_year) if edu else "N/A"
            })
            
    apps_data.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(apps_data), 200

# UPDATE APP STATUS
@app.route('/api/company/applications/<int:app_id>', methods=['PUT'])
@auth_required('session')
def update_application_status(app_id):
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    application = Application.query.get_or_404(app_id)
    
    if application.drive.company_id != current_user.company_profile.company_id: 
        return jsonify({"error": "Unauthorized action."}), 403
        
    if not application.student.user.active:
        return jsonify({"error": "Cannot update status. Student account is suspended by Admin."}), 403
        
    data = request.get_json()
    
    try:
        new_status = ApplicationStatus[data.get('status', '').upper()]
        application.status = new_status
        db.session.commit()
        return jsonify({"message": "Status updated successfully."}), 200
        
    except KeyError: 
        return jsonify({"error": "Invalid status."}), 400

# MANAGE PROFILE
@app.route('/api/company/profile', methods=['GET', 'PUT'])
@auth_required('session')
def manage_company_profile():
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = current_user.company_profile
    
    # get company profile
    if request.method == 'GET':
        return jsonify({
            "name": company.name, 
            "email": current_user.email, 
            "industry": company.industry or "", 
            "hr_contact": company.hr_contact or "", 
            "website": company.website or "", 
            "description": company.description or "", 
            "is_approved": company.is_approved
        }), 200
    
    # update company profile
    if request.method == 'PUT':
        data = request.get_json()
        
        company.name = data.get('name', company.name)
        company.industry = data.get('industry', company.industry)
        company.hr_contact = data.get('hr_contact', company.hr_contact)
        company.website = data.get('website', company.website)
        company.description = data.get('description', company.description)
        
        db.session.commit()
        return jsonify({"message": "Profile updated successfully!", "name": company.name}), 200

# EXPORT CSV
@app.route('/api/company/export-applicants', methods=['POST'])
@auth_required('session')
@email_verification_required
def export_applicants():
    if not current_user.has_role('company'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    company = current_user.company_profile
    
    # trigger background task
    export_company_applicants_csv.delay(company.company_id, current_user.email, company.name)
    
    return jsonify({
        "message": "CSV Export started! Check your email for the attachment soon."
    }), 200



# ==========================================================================================
# STUDENT ENDPOINTS
# ==========================================================================================

# ----------------- 1. STUDENT DASHBOARD -----------------

@app.route('/api/dashboard/student', methods=['GET'])
@auth_required('session')
def student_dashboard_data():
    if not current_user.has_role('student'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = current_user.student_profile
    
    # count active and interview apps
    active_apps_count = Application.query.filter(
        Application.student_id == student.student_id, 
        Application.status != ApplicationStatus.REJECTED
    ).count()
    
    interview_count = Application.query.filter(
        Application.student_id == student.student_id, 
        Application.status == ApplicationStatus.INTERVIEW
    ).count()

    # calc profile completion score
    profile_score = 30 
    if student.resume_url: 
        profile_score += 40
    if student.educations and student.educations[0].verified_edu: 
        profile_score += 30 

    recent_apps = Application.query.filter_by(student_id=student.student_id).order_by(Application.created_at.desc()).all()
    recent_apps_data = []
    applied_drive_ids = []
    
    for app in recent_apps:
        applied_drive_ids.append(app.drive_id)
        recent_apps_data.append({
            "id": app.application_id, 
            "company": app.drive.company.name if app.drive.company else "Unknown", 
            "role": app.drive.job_title, 
            "status": app.status.value,
            "applied_on": safe_format_date(app.created_at)
        })

    # showing only approved and active drives from non-blacklisted companies
    ongoing_query = PlacementDrive.query.join(Company).join(User, Company.user_id == User.id).filter(
        PlacementDrive.is_active == True, 
        PlacementDrive.is_approved == True,
        User.active == True 
    )
    
    if applied_drive_ids: 
        ongoing_query = ongoing_query.filter(~PlacementDrive.drive_id.in_(applied_drive_ids))
        
    ongoing_drives = ongoing_query.order_by(PlacementDrive.created_at.desc()).all()

    ongoing_drives_data = []
    for d in ongoing_drives:
        ongoing_drives_data.append({
            "id": d.drive_id, 
            "company": d.company.name, 
            "industry": d.company.industry, 
            "role": d.job_title, 
            "deadline": safe_format_date(d.deadline)
        })

    return jsonify({
        "user": {
            "name": student.first_name, 
            "full_name": student.full_name
        }, 
        "stats": {
            "active_applications": active_apps_count, 
            "upcoming_interviews": interview_count, 
            "profile_completion": profile_score
        }, 
        "ongoing_drives": ongoing_drives_data, 
        "recent_applications": recent_apps_data
    }), 200

# ----------------- 2. STUDENT APPLICATIONS -----------------

@app.route('/api/student/applications', methods=['GET'])
@auth_required('session')
def get_student_applications():
    # 1. Ensure the user is a student
    if not current_user.has_role('student'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = current_user.student_profile
    
    # 2. Fetch ALL applications using your specific `student_id` column
    all_apps = Application.query.filter_by(
        student_id=student.student_id
    ).order_by(Application.created_at.desc()).all()
    
    applications_data = []
    for app_record in all_apps:
        applications_data.append({
            "id": app_record.application_id,
            "company": app_record.drive.company.name,
            "role": app_record.drive.job_title,
            "applied_on": app_record.created_at.strftime("%b %d, %Y"),
            "status": app_record.status.value,
            
            # Split into explicit categories for the frontend
            "company_details": {
                "name": app_record.drive.company.name,
                "industry": app_record.drive.company.industry,
                "description": app_record.drive.company.description, # Ensure this matches your model!
                "hr_contact": app_record.drive.company.user.email
            },
            "drive_details": {
                "title": app_record.drive.job_title,
                "description": app_record.drive.job_description,
                "deadline": app_record.drive.deadline.strftime("%b %d, %Y")
            }
        })

    return jsonify({"application": applications_data}), 200

# ----------------- 3. STUDENT DRIVES -----------------

@app.route('/api/student/drives', methods=['GET'])
@auth_required('session')
def get_all_student_drives():
    if not current_user.has_role('student'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = current_user.student_profile

    auto_close_expired_drives()    

    drives = PlacementDrive.query.join(Company).join(User, Company.user_id == User.id).filter(
        PlacementDrive.is_active == True, 
        PlacementDrive.is_approved == True,
        User.active == True
    ).all()
    
    user_apps = Application.query.filter_by(student_id=student.student_id).all()
    applied_ids = [app.drive_id for app in user_apps]
    
    edu = student.educations[0] if student.educations else None
    prog = Program.query.get(edu.program_id) if (edu and edu.program_id) else None
    
    student_cgpa = edu.cgpa if edu else None
    student_degree_id = str(prog.degree_id) if prog else None
    student_stream_id = str(prog.stream_id) if prog else None
    is_verified = edu.verified_edu if edu else False

    drives_data = []
    
    for d in drives:
        is_eligible = True
        reasons = []
        
        # check student eligibility for each drive
        if not student.resume_url: 
            is_eligible = False
            reasons.append("Missing Resume")
            
        if not is_verified: 
            is_eligible = False
            reasons.append("Education Unverified")
            
        if d.min_cgpa and (not student_cgpa or student_cgpa < d.min_cgpa): 
            is_eligible = False
            reasons.append(f"{d.min_cgpa}")
            
        if d.allowed_degrees and student_degree_id not in [x.strip() for x in d.allowed_degrees.split(',')]: 
            is_eligible = False
            reasons.append("Degree Mismatch")
            
        if d.allowed_streams and student_stream_id not in [x.strip() for x in d.allowed_streams.split(',')]: 
            is_eligible = False
            reasons.append("Stream Mismatch")

        drives_data.append({
            "id": d.drive_id, 
            "role": d.job_title, 
            "description": d.job_description,
            "eligibility": f"{d.min_cgpa}" if d.min_cgpa else "No minimum CGPA required",
            "deadline": safe_format_date(d.deadline), 
            "company": d.company.name, 
            "industry": d.company.industry,
            "hr_contact": d.company.hr_contact, 
            "company_desc": d.company.description,
            "has_applied": d.drive_id in applied_ids, 
            "is_eligible": is_eligible, 
            "ineligibility_reason": " | ".join(reasons) if not is_eligible else ""
        })
        
    return jsonify({
        "drives": drives_data, 
        "has_resume": bool(student.resume_url)
    }), 200

# APPLY TO DRIVE
@app.route('/api/student/apply/<int:drive_id>', methods=['POST'])
@auth_required('session')
def apply_to_drive(drive_id):
    if not current_user.has_role('student'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = current_user.student_profile
    auto_close_expired_drives() 

    if not student.resume_url or not student.resume_url.strip(): 
        return jsonify({"error": "Please update your profile with a Resume URL."}), 400
        
    if not student.educations or not student.educations[0].verified_edu: 
        return jsonify({"error": "Education must be verified."}), 400
        
    drive = PlacementDrive.query.get(drive_id)
    
    if not drive or not drive.is_active or not drive.is_approved: 
        return jsonify({"error": "Drive is not available."}), 404
        
    if not drive.company.user.active:
        return jsonify({"error": "This drive is no longer accepting applications."}), 403
        
    if Application.query.filter_by(student_id=student.student_id, drive_id=drive_id).first(): 
        return jsonify({"error": "Already applied."}), 400
        
    new_application = Application(
        student_id=student.student_id, 
        drive_id=drive_id, 
        status=ApplicationStatus.APPLIED
    )
    db.session.add(new_application)
    db.session.commit()
    
    return jsonify({"message": f"Successfully applied for {drive.job_title}!"}), 201


# ----------------- 4. STUDENT PROFILE & EXPORTS -----------------

# MANAGE PROFILE
@app.route('/api/student/profile', methods=['GET', 'PUT', 'DELETE'])
@auth_required('session')
def manage_student_profile():
    if not current_user.has_role('student'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = current_user.student_profile
    
    # get profile
    if request.method == 'GET':
        edu = student.educations[0] if student.educations else None
        prog = Program.query.get(edu.program_id) if (edu and edu.program_id) else None
        
        return jsonify({
            "full_name": student.full_name, 
            "uniquifier": current_user.fs_uniquifier, 
            "resume_url": student.resume_url or "",
            "email": current_user.email, 
            "age": int(student.age) if student.age else "",
            "education": {
                "degree": prog.degree.name if prog else "N/A", 
                "degree_id": prog.degree_id if prog else "",
                "stream": prog.stream.name if prog else "N/A", 
                "stream_id": prog.stream_id if prog else "",
                "cgpa": float(edu.cgpa) if edu and edu.cgpa else None,
                "start_year": edu.start_year.strftime('%Y-%m') if edu and edu.start_year else "",
                "end_year": edu.end_year.strftime('%Y-%m') if edu and edu.end_year else "",
                "verified_edu": bool(edu.verified_edu) if edu else False
            }
        }), 200

    # update profile
    if request.method == 'PUT':
        data = request.get_json()
        full_name = data.get('full_name', '').strip()
        
        if full_name and full_name != student.full_name:
            try: 
                validate_official_name(full_name) 
            except ValidationError as e: 
                return jsonify({"error": e.messages[0] if isinstance(e.messages, list) else str(e)}), 400
                
            parts = full_name.split(' ', 1)
            student.first_name = parts[0]
            student.last_name = parts[1] if len(parts) > 1 else ""

        age_val = data.get('age')
        student.age = age_val if age_val else None
        student.resume_url = data.get('resume_url', student.resume_url)
        
        edu_data = data.get('education', {})
        if student.educations:
            edu = student.educations[0]
            changed = False
            
            if edu_data.get('cgpa') and str(edu.cgpa) != str(edu_data['cgpa']): 
                edu.cgpa = edu_data['cgpa']
                changed = True
                
            if edu_data.get('start_year'):
                ns = datetime.strptime(edu_data['start_year'], '%Y-%m').date()
                if not edu.start_year or edu.start_year != ns: 
                    edu.start_year = ns
                    changed = True
                    
            if edu_data.get('end_year'):
                ne = datetime.strptime(edu_data['end_year'], '%Y-%m').date()
                if not edu.end_year or edu.end_year != ne: 
                    edu.end_year = ne
                    changed = True
                    
            deg_id = edu_data.get('degree_id')
            stream_id = edu_data.get('stream_id')
            
            if deg_id and stream_id:
                prog = Program.query.get(edu.program_id) if edu.program_id else None
                if not prog or str(prog.degree_id) != str(deg_id) or str(prog.stream_id) != str(stream_id):
                    new_prog = Program.query.filter_by(degree_id=deg_id, stream_id=stream_id).first()
                    if new_prog: 
                        edu.program_id = new_prog.id
                        changed = True
                        
            if changed: 
                # reverts verification if core academic data is changed
                edu.verified_edu = False 
                
        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully! Admin will verify your education details.", 
            "full_name": student.full_name, 
            "verified_edu": bool(edu.verified_edu)
        }), 200

    # delete account
    if request.method == 'DELETE':
        # clean up all data related to the student
        Application.query.filter_by(student_id=student.student_id).delete()
        Education.query.filter_by(student_id=student.student_id).delete()
        db.session.delete(student)
        
        current_user.roles = []
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        
        return jsonify({"message": "Account successfully deleted."}), 200

# EXPORT CSV
@app.route('/api/student/export-applications', methods=['POST'])
@auth_required('session')
@email_verification_required
def export_applications():
    if not current_user.has_role('student'): 
        return jsonify({"error": "Unauthorized"}), 403
        
    student = current_user.student_profile
    
    # trigger background task
    export_student_applications_csv.delay(student.student_id, current_user.email, student.full_name)
    
    return jsonify({
        "message": "CSV Export started! Check your email for the attachment soon."
    }), 200