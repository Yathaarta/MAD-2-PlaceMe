from email.message import EmailMessage
import smtplib
import os, csv
from datetime import datetime
from celery import shared_task

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

@shared_task
def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg['Subject'] = "PlaceMe - Verification Code"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg.set_content(f"Your PlaceMe verification code is: {otp}\n\nThis code is valid for 10 minutes. Do not share it with anyone.")

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
    """
    Generates a CSV of all student applications in the background,
    and sends a REAL email alert with the CSV file attached.
    """
    from app import app 
    from models.dbmodel import Application
    
    with app.app_context():
        applications = Application.query.filter_by(student_id=student_id).all()
        
        # makedir static/exports if not exist already
        export_dir = os.path.join(app.root_path, 'static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # 2. getting filename and path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"applications_export_{student_id}_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        # making csv
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
        
        # constructing email
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
    """
    Generates a CSV of all applicants that applied for different job roles in a company,
    and sends a REAL email alert with the CSV file attached.
    """
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
        
        # making csv
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
        
        # constructing email
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

        # deleting file cause don't want to store it permanently on server    
        os.remove(filepath)
        return filepath
    