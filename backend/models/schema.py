from marshmallow import Schema, fields, validate, ValidationError
import re


def validate_official_name(name):
   
    if not name:
        raise ValidationError("Name is required.")

    # initials not allowed in name - hence no '.' char
    if "." in name:
        raise ValidationError("Initials are not allowed in Name. Please use full name.")

    # [a-zA-Z\s]+$ means start to end, only letters and spaces
    if not re.match(r"^[a-zA-Z\s]+$", name):
        raise ValidationError("Name contains invalid characters, numbers, or hyphens.")
    
    parts = name.split() 
    # name should only have max 4 parts eg. Ursula von der leyen 
    if len(parts) > 4:
        raise ValidationError("Please provide only First, Middle, and Last name.")
    
    # the first name should atleast have min lenght 3 eg. Jay and rest must have atleast 2 length
    for i in range(len(parts)):
        if i == 0:
            if len(parts[i])<3:
               raise ValidationError(f"Name '{parts[i]}' is too short.")
            elif len(parts[i])>20:
                raise ValidationError(f"'{parts[i]}' is too long.")
        else:
            if len(parts[i])<2:
                raise ValidationError(f"Name '{parts[i]}' in '{' '.join(parts)}' is too short.")
    


def safe_format_date(dt):
    # Safely formats a datetime or date object into a readable string
    if not dt: 
        return "TBD"
    if hasattr(dt, 'strftime'): 
        return dt.strftime('%b %d, %Y')
    return str(dt)[:10]



def get_names_from_ids(model, id_string):
    
    # Converts comma-separated string of Ids (eg "1,2") into a list of names from the corresponding Database table.
   
    if not id_string: 
        return []
    try:
        # converts "1, 2" -> [1, 2]
        id_list = [int(x.strip()) for x in id_string.split(',') if x.strip().isdigit()]
        if not id_list:
            return []
    
        # Query the database for matches
        items = model.query.filter(model.id.in_(id_list)).all()
        return [item.name for item in items]
    except Exception as e:
        print(f"Error resolving names for IDs {id_string}: {e}")
        return []
    



# 1. student registration schema
class StudentRegisterSchema(Schema):
    full_name = fields.String(
        required=True, 
        validate=validate_official_name,    # custom error for name
        error_messages={
            "required": "Full Name is required.", 
            "invalid": "Please provide a valid full name."
        }
    )
    
    email = fields.String(
        required=True, 
        #validate 
        error_messages={
            "required": "Email address is required.", 
            "invalid": "Invalid email format."
        }
    )
    
    password = fields.String(
        required=True, 
        validate=validate.Length(min=6, error="Password must be at least 6 characters long."),
        error_messages={
            "required": "Password is required."
        }
    )
    
    degree = fields.Integer(
        required=True,
        error_messages={"required": "Please select a Degree."}
    )
    
    stream = fields.Integer(
        required=True,
        error_messages={"required": "Please select a Stream."}
    )
    
    # handling unknown fields - strip them instead of erroring
    class Meta:
        unknown = 'exclude'

# company registeration schema
class CompanyRegisterSchema(Schema):
    company_name = fields.String(
        required=True, 
        validate=validate.Length(min=2),
        error_messages={"required": "Company Name is required."}
    )
    
    hr_email = fields.String(
        required=True, 
        # validate=validate_real_email, 
        error_messages={"required": "HR Email is required.", "invalid": "Invalid email."}
    )
    
    password = fields.String(
        required=True, 
        validate=validate.Length(min=6, error="Password must be at least 6 characters."),
        error_messages={"required": "Password is required."}
    )
    
    industry = fields.String(
        required=True,
        error_messages={"required": "Please select an Industry."}
    )
    
    # Optional fields
    location = fields.String()
    website = fields.String()

    class Meta:
        unknown = 'exclude'