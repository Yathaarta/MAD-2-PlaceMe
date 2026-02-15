import os
from app import app, db, user_datastore 
from models.dbmodel import *


def seed_academic_data():
    print("Seeding Academic Data...")

    # 1. Degrees
    degrees_data = ["B.Tech", "M.Tech", "MBA", "BBA", "Diploma"]
    degree_objs = {} # Map name -> object

    for d_name in degrees_data:
        deg = Degree.query.filter_by(name=d_name).first()
        if not deg:
            deg = Degree(name=d_name) # type: ignore
            db.session.add(deg)
            print("Academic Data Seeded! 1 : Degrees added")
        degree_objs[d_name] = deg
    
    db.session.commit()

    # 2. Streams (and their codes)
    streams_data = [
        ("Computer Science", "CSE"),
        ("Mechanical Engineering", "MECH"),
        ("Civil Engineering", "CIVIL"),
        ("Electronics & Comm", "ECE"),
        ("Finance", "FIN"),
        ("Human Resources", "HR"),
        ("Marketing", "MKT"),
        ("Business Analytics", "BA")
    ]
    stream_objs = {} # Map code -> object

    for s_name, s_code in streams_data:
        stream = Stream.query.filter_by(code=s_code).first()
        if not stream:
            stream = Stream(name=s_name, code=s_code) # type: ignore
            db.session.add(stream)
            print("Academic Data Seeded! 2 : Streams added")
        stream_objs[s_code] = stream
    
    db.session.commit()

    # 3. Programs (Valid Combinations)
    # Define which degrees allow which streams
    programs_map = [
        ("B.Tech", ["CSE", "MECH", "CIVIL", "ECE"]),
        ("M.Tech", ["CSE", "MECH", "ECE"]),
        ("Diploma", ["MECH", "CIVIL"]),
        ("MBA", ["FIN", "HR", "MKT", "BA"]),
        ("BBA", ["FIN", "MKT"])
    ]

    for deg_name, stream_codes in programs_map:
        deg = degree_objs[deg_name]
        for s_code in stream_codes:
            stream = stream_objs[s_code]
            # Check if program exists
            prog = Program.query.filter_by(degree_id=deg.id, stream_id=stream.id).first()
            if not prog:
                prog = Program(degree_id=deg.id, stream_id=stream.id) # type: ignore
                db.session.add(prog)
                print("Academic Data Seeded! 3 : Programs added")
    
    db.session.commit()
    print("Academic Data present.")


def init_database():

    with app.app_context():

        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')           
        db_filename = db_uri.replace('sqlite:///', '')  # type:ignore
        db_file_path = os.path.join(app.instance_path, db_filename)  
        db_existed_bef_create_all = os.path.exists(db_file_path)  
        # needed to check if db being created first time or already exists so only add dummy data first time

        db.create_all()
        print('Database tables created.')
        # ---------- create roles in Role table ----------

        if not Role.query.filter_by(name='admin').first():
            user_datastore.create_role(name='admin', description='Administrator')
        
        if not Role.query.filter_by(name='student').first():
            user_datastore.create_role(name='student', description='Student User')
            
        if not Role.query.filter_by(name='company').first():
            user_datastore.create_role(name='company', description='Company Rep')
        
        # ---------- creating admin ------------

        admin_email = os.getenv('ADMIN_EMAIL')
        admin_passwd = os.getenv('ADMIN_PASSWORD')
        admin_uniquifier = os.getenv('ADMIN_UNIQE_ID')
        admin_user = user_datastore.find_user(email = admin_email)

        if not admin_user:
            user_datastore.create_user(
                email = admin_email,
                password = admin_passwd,
                roles = ['admin'],
                active=True,
                fs_uniquifier = admin_uniquifier
            )
            print(f"Superuser created: {admin_email}")

        elif not admin_user.has_role('admin'):
            user_datastore.add_role_to_user(admin_user, 'admin')
            print(f"Fixed: Added 'admin' role to {admin_email}")
        
        db.session.commit()
        print("Database Seed Complete!")

        # ----------- for dummy data addition -------------
        seed_academic_data()
        # will do later after apis and frontend made for testing
        
if __name__ == '__main__':
    init_database()