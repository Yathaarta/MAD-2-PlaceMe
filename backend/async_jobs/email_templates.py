from jinja2 import Template


# ================= BASE TEMPLATE =================
def get_base_html_template(title, content_html):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
        @media only screen and (max-width:600px){{
            .col {{ display:block !important; width:100% !important; }}
        }}
        </style>
    </head>

    <body style="margin:0;background:#2b2f34;color:#e6e6e6;font-family:Segoe UI, Tahoma, sans-serif;">

    <div style="padding:15px 6px;">
    <div style="max-width:600px;margin:auto;background:#3a3f45;border-radius:12px;overflow:hidden;">

        <div style="background:linear-gradient(135deg,#306893,#4c9472);padding:25px;text-align:center;">
            <h1 style="margin:0;color:#fff;">PlaceMe</h1>
            <p style="margin:5px 0 0;color:#e0f2fe;font-size:13px;">
                Campus Placement Portal
            </p>
        </div>

        <div style="padding:20px 10px;">
            {content_html}
        </div>

        <div style="background:#2b2f34;padding:15px;text-align:center;border-top:1px solid #444;">
            <p style="margin:0;font-size:12px;color:#9ca3af;">
                This is an automated message. Please do not reply.
            </p>
        </div>

    </div>
    </div>

    </body>
    </html>
    """


# ================= COMMON BLOCKS =================

def _render_stat_grid(stats):
    template = Template("""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0; table-layout:fixed;">
    {% for row in stats|batch(3, fill_with=None) %}
    <tr>
        {% for item in row %}
            {% if item %}
            <td class="col" width="33.33%" valign="top">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:5px;">
                    <tr>
                        <td style="
                            background:#2b2f34;
                            padding:18px 10px;
                            border-radius:10px;
                            border-top:3px solid {{item.color}};
                            text-align:center;
                        ">
                            <h2 style="margin:0;color:{{item.color}};">{{item.value}}</h2>
                            <p style="margin:5px 0 0;">{{item.label}}</p>
                        </td>
                    </tr>
                </table>
            </td>
            {% endif %}
        {% endfor %}
    </tr>
    {% endfor %}
    </table>
    """)
    return template.render(stats=stats)


def _render_button():
    return """
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:30px;">
    <tr>
        <td align="center">
            <table cellpadding="0" cellspacing="0">
                <tr>
                    <td style="background:linear-gradient(135deg,#306893,#4c9472);border-radius:8px;">
                        <a href="" style="
                            display:inline-block;
                            padding:12px 20px;
                            color:#ffffff;
                            text-decoration:none;
                            font-weight:600;
                        ">
                            Go to your account
                        </a>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    </table>
    """


# ================= YOUR ORIGINAL FUNCTIONS (UNCHANGED NAMES) =================

def get_otp_html(otp_code):
    content = f"""
        <h2>🔐 Secure Verification</h2>

        <div style="
            background:#2b2f34;
            border:2px dashed #4c9472;
            border-radius:10px;
            padding:25px;
            text-align:center;
            margin:25px 0;
        ">
            <span style="font-size:34px;letter-spacing:8px;color:#4c9472;">
                {otp_code}
            </span>
        </div>

        <p style="color:#f87171;">⚠ This code will expire in 10 minutes.</p>

        {_render_button()}
    """
    return get_base_html_template("Your Verification Code", content)


def get_csv_export_html(recipient_name, record_type):
    content = f"""
        <h2>📦 Your Data Export is Ready</h2>

        <p>Hello <strong>{recipient_name}</strong>,</p>

        <p>Your requested data for <strong>{record_type}</strong> is ready.</p>

        <div style="
            background:#2b2f34;
            border-left:4px solid #4c9472;
            padding:15px;
            margin:20px 0;
            border-radius:8px;
        ">
            📄 File is attached with this email.
        </div>

        {_render_button()}
    """
    return get_base_html_template("Your Data Export", content)


def get_student_report_html(student_name, month_name, total_applied, total_interview, total_selected):
    stats = [
        {"value": total_applied, "label": "Applied", "color": "#4c9472"},
        {"value": total_interview, "label": "Interviews", "color": "#306893"},
        {"value": total_selected, "label": "Selected", "color": "#22c55e"},
    ]

    content = f"""
        <h2>Your Monthly Insights</h2>
        <p>Hello <strong>{student_name}</strong>,</p>

        {_render_stat_grid(stats)}

        {_render_button()}
    """
    return get_base_html_template(f"{month_name} Report", content)


def get_company_report_html(company_name, month_name, total_drives, total_apps, total_selected):
    stats = [
        {"value": total_drives, "label": "Drives", "color": "#06b6d4"},
        {"value": total_apps, "label": "Applications", "color": "#306893"},
        {"value": total_selected, "label": "Hires", "color": "#22c55e"},
    ]

    content = f"""
        <h2>Monthly Recruitment Summary</h2>
        <p>Hello <strong>{company_name}</strong> Team,</p>

        {_render_stat_grid(stats)}

        {_render_button()}
    """
    return get_base_html_template(f"{month_name} Recruitment Report", content)


def get_admin_report_html(month_name, new_users, new_companies, new_drives, new_apps):
    stats = [
        {"value": new_users, "label": "Students", "color": "#306893"},
        {"value": new_companies, "label": "Companies", "color": "#a855f7"},
        {"value": new_drives, "label": "Drives", "color": "#06b6d4"},
        {"value": new_apps, "label": "Applications", "color": "#22c55e"},
    ]

    content = f"""
        <h2>Platform Growth Summary</h2>
        <p>Hello <strong>Admin</strong>,</p>

        {_render_stat_grid(stats)}

        {_render_button()}
    """
    return get_base_html_template(f"Admin Summary - {month_name}", content)