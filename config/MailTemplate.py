import os


def generate_email_template(user_id: int) -> str:

    return f'''<!DOCTYPE HTML>
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml"
        xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="x-apple-disable-message-reformatting">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Verify your email</title>
        <style type="text/css">
            a {{ text-decoration: none !important; color: #0000EE; }}
            p {{ font-size: 15px; line-height: 24px; font-family: 'Helvetica', Arial, sans-serif; color: #000000; }}
            h1 {{ font-size: 22px; font-family: 'Helvetica', Arial, sans-serif; color: #000000; }}
        </style>
    </head>
    <body style="text-align: center; background-color: #f2f4f6; color: #000000">
        <div style="text-align: center;">
            <img style="max-width: 600px; max-height: 850px;" src="https://img.freepik.com/free-vector/welcome-concept-illustration_114360-27147.jpg" alt="Hero image">
            <table align="center" style="width: 600px; background-color: #ffffff;">
                <tr>
                    <td style="padding: 30px;">
                        <h1>Finish creating your account</h1>
                        <p>To validate your account and activate your ability to detect deepfakes, please complete your profile by clicking the link below</p>
                        <a href="{os.getenv("BASE_URL")}/api/v1/webhooks/verify-email/{user_id}" style="background-color: #000000; padding: 12px 15px; color: #ffffff; border-radius: 25px;">Confirm email address</a>
                        <p>If you did not associate your address with a DFD account, please ignore this message and do not click on the link above.</p>
                    </td>
                </tr>
            </table>
            <table align="center" style="width: 600px; background-color: #000000;">
                <tr>
                    <td style="padding: 30px; color: #ffffff;">
                        <p><a href="" style="color: #ffffff;">dfd.onrender.com</a></p>
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>'''
