import enum
from flask_sqlalchemy import SQLAlchemy
from flask_security.core import UserMixin, RoleMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timezone

db = SQLAlchemy()


class ApplicationStatus(enum.Enum):
    APPLIED = "Applied"
    SHORTLISTED = "Shortlisted"
    INTERVIEW = "Interview"
    SELECTED = "Selected"
    REJECTED = "Rejected"


class TimestampMixin(object):
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())

    roles = db.relationship(
        'Role',
        secondary='roles_users',
        backref=db.backref('users', lazy='dynamic')
    )   # type: ignore

    student_profile = db.relationship(
        'StudentProfile',
        backref='user',
        uselist=False,
        cascade="all, delete-orphan"
    )

    company_profile = db.relationship(
        'Company',
        backref='user',
        uselist=False,
        cascade="all, delete-orphan"
    )


class Company(db.Model, TimestampMixin):
    __tablename__ = 'company_profile'

    company_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100))
    hr_contact = db.Column(db.String(300))
    website = db.Column(db.String(2085))
    description = db.Column(db.Text)

    is_approved = db.Column(db.Boolean, default=False, nullable=False)

    drives = db.relationship(
        'PlacementDrive',
        backref='company',
        lazy=True,
        cascade="all, delete-orphan"
    )


class StudentProfile(db.Model, TimestampMixin):
    __tablename__ = 'student_profile'

    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))

    age = db.Column(db.Numeric(2, 0))
    resume_url = db.Column(db.String(2085))

    educations = db.relationship(
        'Education',
        backref='student',
        lazy=True,
        cascade="all, delete-orphan"
    )

    applications = db.relationship(
        'Application',
        backref='student',
        lazy=True,
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() if self.last_name else self.first_name


class Degree(db.Model):
    __tablename__ = 'degree'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    programs = db.relationship('Program', backref='degree', lazy=True)


class Stream(db.Model):
    __tablename__ = 'stream'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    programs = db.relationship('Program', backref='stream', lazy=True)


class Program(db.Model):
    __tablename__ = 'program'

    id = db.Column(db.Integer, primary_key=True)
    degree_id = db.Column(db.Integer, db.ForeignKey('degree.id'), nullable=False)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('degree_id', 'stream_id', name='_degree_stream_uc'),
    )


class Education(db.Model):
    __tablename__ = 'education'

    edu_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profile.student_id"),
        nullable=False
    )
    program_id = db.Column(
        db.Integer,
        db.ForeignKey('program.id'),
        nullable=False
    )

    cgpa = db.Column(db.Numeric(3, 2))
    start_year = db.Column(db.Date)
    end_year = db.Column(db.Date)

    verified_edu = db.Column(db.Boolean, default=False, nullable=False)


class PlacementDrive(db.Model, TimestampMixin):
    __tablename__ = 'placement_drive'

    drive_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company_profile.company_id"),
        nullable=False
    )

    job_title = db.Column(db.String(100))
    job_description = db.Column(db.Text)

    min_cgpa = db.Column(db.Numeric(3, 2))
    allowed_degrees = db.Column(db.String(100))
    allowed_streams = db.Column(db.String(200))

    deadline = db.Column(db.Date)

    is_active = db.Column(db.Boolean, default=True, nullable=False) 
    is_approved = db.Column(db.Boolean, default=False, nullable=False)

    applications = db.relationship(
        'Application',
        backref='drive',
        lazy=True,
        cascade="all, delete-orphan"
    )


class Application(db.Model, TimestampMixin):
    __tablename__ = 'job_applications'

    application_id = db.Column(db.Integer, primary_key=True)

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey('placement_drive.drive_id'),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profile.student_id"),
        nullable=False
    )

    status = db.Column(
        db.Enum(ApplicationStatus),
        default=ApplicationStatus.APPLIED,
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint('drive_id', 'student_id', name='_drive_student_uc'),
    )