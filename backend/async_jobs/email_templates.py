def get_base_html_template(title, content_html):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>

        <style>
            @media only screen and (max-width: 600px) {{

                .container {{
                    width: 100% !important;
                    border-radius: 0 !important;
                }}

                .content {{
                    padding: 20px 12px !important;
                }}

                .col {{
                    display: block !important;
                    width: 100% !important;
                }}
            }}
        </style>
    </head>

    <body style="
        margin:0;
        padding:0;
        background:#2b2f34;
        font-family:Segoe UI, Tahoma, sans-serif;
        color:#e6e6e6;
    ">

        <div style="padding:15px 6px;">
            <div class="container" style="
                max-width:600px;
                margin:auto;
                background:#3a3f45;
                border-radius:14px;
                overflow:hidden;
                box-shadow:0 10px 30px rgba(0,0,0,0.5);
            ">

                <!-- HEADER -->
                <div style="
                    background:linear-gradient(135deg, #306893 0%, #4c9472 100%);
                    padding:25px;
                    text-align:center;
                ">
                    <h1 style="margin:0; color:#fff;">PlaceMe</h1>
                    <p style="margin:5px 0 0; color:#e0f2fe; font-size:13px;">
                        Campus Placement Portal
                    </p>
                </div>

                <!-- BODY -->
                <div class="content" style="padding:20px 10px;">
                    {content_html}
                </div>

                <!-- FOOTER -->
                <div style="
                    background:#2b2f34;
                    padding:15px;
                    text-align:center;
                    border-top:1px solid #444;
                ">
                    <p style="margin:0; font-size:12px; color:#9ca3af;">
                        This is an automated message. Please do not reply.
                    </p>
                </div>

            </div>
        </div>
    </body>
    </html>
    """


def button_block():
    return """
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:30px;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="center" style="
                            background: linear-gradient(135deg, #306893 0%, #4c9472 100%);
                            border-radius: 8px;
                        ">
                            <a href="" style="
                                display: inline-block;
                                padding: 12px 20px;
                                color: #ffffff;
                                text-decoration: none;
                                font-weight: 600;
                                font-size: 14px;
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


def three_col_block(v1, l1, c1, v2, l2, c2, v3, l3, c3):
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0; table-layout:fixed;">
        <tr>

            <td class="col" width="33.33%" valign="top">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:5px;">
                    <tr>
                        <td style="
                            background:#2b2f34;
                            padding:18px 10px;
                            border-radius:10px;
                            border-top:3px solid {c1};
                            text-align:center;
                        ">
                            <h2 style="margin:0;color:{c1};">{v1}</h2>
                            <p style="margin:5px 0 0;">{l1}</p>
                        </td>
                    </tr>
                </table>
            </td>

            <td class="col" width="33.33%" valign="top">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:5px;">
                    <tr>
                        <td style="
                            background:#2b2f34;
                            padding:18px 10px;
                            border-radius:10px;
                            border-top:3px solid {c2};
                            text-align:center;
                        ">
                            <h2 style="margin:0;color:{c2};">{v2}</h2>
                            <p style="margin:5px 0 0;">{l2}</p>
                        </td>
                    </tr>
                </table>
            </td>

            <td class="col" width="33.33%" valign="top">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:5px;">
                    <tr>
                        <td style="
                            background:#2b2f34;
                            padding:18px 10px;
                            border-radius:10px;
                            border-top:3px solid {c3};
                            text-align:center;
                        ">
                            <h2 style="margin:0;color:{c3};">{v3}</h2>
                            <p style="margin:5px 0 0;">{l3}</p>
                        </td>
                    </tr>
                </table>
            </td>

        </tr>
    </table>
    """


def get_otp_html(otp_code):
    content = f"""
        <h2>🔐 Secure Verification</h2>

        <p>Use the code below:</p>

        <div style="
            background:#2b2f34;
            border:2px dashed #4c9472;
            border-radius:10px;
            padding:25px;
            text-align:center;
            margin:25px 0;
        ">
            <span style="font-size:34px; letter-spacing:8px; color:#4c9472;">
                {otp_code}
            </span>
        </div>

        <p style="color:#f87171;">⚠ Expires in 10 minutes</p>

        {button_block()}
    """
    return get_base_html_template("Verification Code", content)


def get_csv_export_html(recipient_name, record_type):
    content = f"""
        <h2>📦 Data Export Ready</h2>

        <p>Hello <strong>{recipient_name}</strong>,</p>

        <div style="
            background:#2b2f34;
            border-left:4px solid #4c9472;
            padding:15px;
            margin:20px 0;
            border-radius:8px;
        ">
            📄 File is attached with this email.
        </div>

        {button_block()}
    """
    return get_base_html_template("Export Ready", content)


def get_student_report_html(name, month, a, i, s):
    content = f"""
        <h2>Monthly Report</h2>
        <p>Hello <strong>{name}</strong>,</p>

        {three_col_block(a,"Applied","#4c9472", i,"Interviews","#306893", s,"Selected","#22c55e")}

        {button_block()}
    """
    return get_base_html_template(month, content)


def get_company_report_html(name, month, d, a, s):
    content = f"""
        <h2>Company Report</h2>
        <p>Hello <strong>{name}</strong>,</p>

        {three_col_block(d,"Drives","#06b6d4", a,"Applications","#306893", s,"Hires","#22c55e")}

        {button_block()}
    """
    return get_base_html_template(month, content)


def get_admin_report_html(month, u, c, d, a):
    content = f"""
        <h2>Admin Summary</h2>

        {three_col_block(u,"Users","#306893", c,"Companies","#a855f7", d,"Drives","#06b6d4")}
        {three_col_block(a,"Applications","#22c55e", "","","#000", "","","#000")}

        {button_block()}
    """
    return get_base_html_template(month, content)