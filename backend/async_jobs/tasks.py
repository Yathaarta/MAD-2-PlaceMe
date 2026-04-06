import os, csv
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from celery import shared_task

from dotenv import load_dotenv
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

from async_jobs.email_templates import (get_otp_html, 
    get_csv_export_html, get_student_report_html,
    get_company_report_html, get_admin_report_html
)

# ----------------- HELPER FUCNTIONS -----------------

def send_report_email(to_email, subject, plain_text, html_content):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg.set_content(plain_text)
    msg.add_alternative(html_content, subtype='html')

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)   # type: ignore
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send report email to {to_email}: {e}")


def get_last_month_dates():
    today = datetime.now()
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = first_of_this_month - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return last_month_start, last_month_end, last_month_start.strftime("%B %Y")


# ----------------- SCHEDULED MONTHLY TASKS -----------------


@shared_task(name='send_monthly_student_reports')
def send_monthly_student_reports():
    from app import app
    from models.dbmodel import StudentProfile, Application
    
    start_date, end_date, month_name = get_last_month_dates()
    
    with app.app_context():
        students = StudentProfile.query.all()
        for student in students:
            if not student.user.active or not student.user.confirmed_at:
                continue
                
            apps = Application.query.filter(
                Application.student_id == student.student_id,
                Application.created_at >= start_date,
                Application.created_at <= end_date
            ).all()
            
            total_applied = len(apps) if apps else 0
            total_interview = sum(1 for app in apps if app.status.value == "Interview") if apps else 0
            total_selected = sum(1 for app in apps if app.status.value == "Selected") if apps else 0
            
            html_content = get_student_report_html(student.first_name, month_name, total_applied, total_interview, total_selected)
            plain_text = f"Your {month_name} Report: Applied: {total_applied}, Interviews: {total_interview}, Selected: {total_selected}"
            send_report_email(student.user.email, f"Your PlaceMe {month_name} Report", plain_text, html_content)
    
    return "Student reports sent."


@shared_task(name='send_monthly_company_reports')
def send_monthly_company_reports():
    from app import app
    from models.dbmodel import Company, PlacementDrive, Application
    
    start_date, end_date, month_name = get_last_month_dates()
    
    with app.app_context():
        companies = Company.query.all()
        for company in companies:
            if not company.user.active or not company.is_approved or not company.user.confirmed_at:
                continue
                
            drives = PlacementDrive.query.filter(
                PlacementDrive.company_id == company.company_id,
                PlacementDrive.created_at >= start_date,
                PlacementDrive.created_at <= end_date
            ).all()
            
            apps = Application.query.join(PlacementDrive).filter(
                PlacementDrive.company_id == company.company_id,
                Application.created_at >= start_date,
                Application.created_at <= end_date
            ).all()
            
            total_drives = len(drives) if drives else 0
            total_apps = len(apps) if apps else 0
            total_selected = sum(1 for app in apps if app.status.value == "Selected") if apps else 0
            
            html_content = get_company_report_html(company.name, month_name, total_drives, total_apps, total_selected)
            plain_text = f"Company Report {month_name}: {total_drives} New Drives, {total_apps} Applications, {total_selected} Selected."
            send_report_email(company.user.email, f"PlaceMe {month_name} Recruitment Summary", plain_text, html_content)

    return "Company reports sent."


@shared_task(name='send_monthly_admin_reports')
def send_monthly_admin_reports():
    from app import app
    from models.dbmodel import User, Role, PlacementDrive, Application
    
    start_date, end_date, month_name = get_last_month_dates()
    
    with app.app_context():
        admin_role = Role.query.filter_by(name='admin').first()
        admins = User.query.filter(User.roles.contains(admin_role)).all() # type: ignore
        
        if not admins:
            return "No admins found."
            
        new_users = User.query.filter(User.roles.any(name='student'), User.confirmed_at >= start_date, User.confirmed_at <= end_date).count() # type: ignore
        new_comps = User.query.filter(User.roles.any(name='company'), User.confirmed_at >= start_date, User.confirmed_at <= end_date).count() # type: ignore
        
        new_drives = PlacementDrive.query.filter(PlacementDrive.created_at >= start_date, PlacementDrive.created_at <= end_date).count()
        new_apps = Application.query.filter(Application.created_at >= start_date, Application.created_at <= end_date).count()
        
        html_content = get_admin_report_html(month_name, new_users, new_comps, new_drives, new_apps)
        plain_text = f"Admin Report {month_name} | New Students: {new_users} | New Companies: {new_comps} | Drives: {new_drives} | Apps: {new_apps}"
        
        for admin in admins:
            if not admin.confirmed_at:
                continue
            send_report_email(admin.email, f"PlaceMe Platform Growth - {month_name}", plain_text, html_content)

    return "Admin reports sent."


# ----------------- OTP & EXPORT CSV -----------------

@shared_task
def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg['Subject'] = "PlaceMe - Verification Code"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg.set_content(f"Your PlaceMe verification code is: {otp}\n\nThis code is valid for 10 minutes. Do not share it with anyone.")
    
    html_content = get_otp_html(otp)
    msg.add_alternative(html_content, subtype='html')

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)   # type: ignore
        server.send_message(msg)
        server.quit()
        return f"OTP successfully sent to {to_email}"
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

@shared_task
def export_student_applications_csv(student_id, email, student_name):
    from app import app 
    from models.dbmodel import Application
    
    with app.app_context():
        applications = Application.query.filter_by(student_id=student_id).all()
        
        export_dir = os.path.join(app.root_path, 'static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"applications_export_{student_id}_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Company Name', 'Job Role', 'Status', 'Applied On', 'Drive Deadline'])
            
            for app_record in applications:
                drive = app_record.drive
                company = drive.company
                writer.writerow([
                    company.name,
                    drive.job_title,
                    app_record.status.value,
                    app_record.created_at.strftime("%b %d, %Y"),
                    drive.deadline.strftime("%b %d, %Y") if drive.deadline else "TBD"
                ])
        
        msg = EmailMessage()
        msg['Subject'] = "PlaceMe - Your CSV Export is Ready"
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
        email_body = (
            f"Hello {student_name},\n\n"
            f"Your requested application history export has been generated successfully.\n"
            f"Please find your CSV file attached to this email.\n\n"
            f"Best regards,\n"
            f"The PlaceMe Team"
        )
        msg.set_content(email_body)

        html_content = get_csv_export_html(student_name, "application history")
        msg.add_alternative(html_content, subtype='html')

        with open(filepath, 'rb') as f:
            csv_data = f.read()
            
        msg.add_attachment(
            csv_data,
            maintype='text',
            subtype='csv',
            filename=filename
        )

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)   # type: ignore
            server.send_message(msg)
            server.quit()
            print(f"CSV Export successfully emailed to {email} with attachment.")
        except Exception as e:
            print(f"Failed to send CSV export email: {e}")
            
        os.remove(filepath)
        return filepath


@shared_task
def export_company_applicants_csv(company_id, email, company_name):
    from app import app 
    from models.dbmodel import Application,PlacementDrive,Program

    with app.app_context():
        applicants = Application.query.join(PlacementDrive).filter(
            PlacementDrive.company_id == company_id
        ).all()
        
        export_dir = os.path.join(app.root_path, 'static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"applications_export_{company_id}_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Candidate Name',
                'Candidate Email',
                'Age',
                'Role Applied',
                'Applied on',
                'Degree & Stream',
                'Degree Duration',
                'CGPA',
                'Status',
                'Resume'])
            
            for app in applicants:
                student = app.student
                edu = student.educations[0] if student.educations else None
                prog = Program.query.get(edu.program_id) if edu and edu.program_id else None
                
                writer.writerow([
                    student.full_name, 
                    student.user.email,
                    int(student.age) if student.age else None,
                    app.drive.job_title, 
                    app.created_at.strftime("%b %d, %Y"),
                    f"{prog.degree.name if prog else 'N/A'}, {prog.stream.name if prog else 'N/A'}",
                    f"{edu.start_year.strftime('%Y') if edu else 'N/A'} - {edu.end_year.strftime('%Y') if edu else 'N/A'}",
                    float(edu.cgpa) if edu and edu.cgpa else "N/A",
                    app.status.value, 
                    student.resume_url, 
                ])
        
        msg = EmailMessage()
        msg['Subject'] = "PlaceMe - Your CSV Export is Ready"
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
        email_body = (
            f"Hello {company_name},\n\n"
            f"Your requested applicant details export has been generated successfully.\n"
            f"Please find your CSV file attached to this email.\n\n"
            f"Best regards,\n"
            f"The PlaceMe Team"
        )
        msg.set_content(email_body)

        html_content = get_csv_export_html(company_name, "applicant tracking records")
        msg.add_alternative(html_content, subtype='html')

        with open(filepath, 'rb') as f:
            csv_data = f.read()
            
        msg.add_attachment(
            csv_data,
            maintype='text',
            subtype='csv',
            filename=filename
        )

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)   # type: ignore
            server.send_message(msg)
            server.quit()
            print(f"CSV Export successfully emailed to {email} with attachment.")
        except Exception as e:
            print(f"Failed to send CSV export email: {e}")

        os.remove(filepath)
        return filepath