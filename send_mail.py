import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import os

# should be passed through environment variables
username = os.environ.get('EMAIL_USER')
password = os.environ.get('EMAIL_PW')

def send_mail(text='Email Body', subject='Hello World', from_email='',
              to_emails=None, html_file_path=None, html=None, html_inserts=None, image_file_paths=None):
    assert isinstance(to_emails, list)


    # EMAIL OBJECT
    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = ",".join(to_emails)
    msg['Subject'] = subject

    txt_part = MIMEText(text, 'plain')
    msg.attach(txt_part)

    # attach html
    if html_file_path is not None:
        if os.path.isfile(html_file_path):
            with open(html_file_path, 'r') as f:
                html = f.read()

            if html_inserts is not None:
                html = html.format(**html_inserts)
            html_part = MIMEText(html, 'html')
            msg.attach(html_part)
        else:
            raise Exception("html_file_path is incorrect.")
    elif html is not None:

            if html_inserts is not None:
                if not isinstance(html_inserts, dict):
                    raise Exception("html_inserts is not a dictionary")
                html = html.format(**html_inserts)

            html_part = MIMEText(html, 'html')
            msg.attach(html_part)

    # attach images - embedded
    if html_inserts is not None:
        if isinstance(html_inserts, dict):

            keys_str = " ".join(list(html_inserts.keys()))
            keys = list(html_inserts.keys())
            if 'cid' in keys_str:
                for key in keys:
                    if 'cid' in key:
                        cid = html_inserts[key]
                        path = html_inserts[key]
                        if os.path.isfile(path):
                            with open(path, 'rb') as f:
                                image = f.read()
                                image_name = f.name

                            image_part = MIMEImage(image, name=image_name)
                            image_part.add_header('Content-ID', f"<{cid}>")
                            msg.attach(image_part)
                        else:
                            raise Exception(f"{path} is not a correct file path.")
        else:
            raise Exception("html_inserts has to be a dictionary.")

    # attach image - not embedded
    elif image_file_paths is not None:
        if isinstance(image_file_paths, list):
            for path in image_file_paths:
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        image = f.read()
                        image_name = f.name
                    image_part = MIMEImage(image, name=image_name)
                    msg.attach(image_part)
                else:
                    raise Exception(f"{path} is not a correct file path.")
        elif isinstance(image_file_paths, str):
            if os.path.isfile(image_file_paths):
                with open(image_file_paths, 'rb') as f:
                    image = f.read()
                    image_name = f.name
                image_part = MIMEImage(image, name=image_name)
                msg.attach(image_part)
        else:
            raise Exception("Image file paths is not of the correct format. Must be a string or list.")


    msg_str = msg.as_string()

    # SEND EMAIL
    # login to my smtp server:
    # 1 create server, 2 configure(ehlo), 3 secure(starttls), 4 login
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()  # identifies with server
    server.starttls()  # creates a secure connection
    server.ehlo()  # identifies with server as encrypted connection

    server.login(username, password)  # login
    server.sendmail(from_email, to_emails, msg_str)
    server.quit()


if __name__ == "__main__":
    to_emails = ['something@gmail.com']

    image_path = "images/facebook_logo.png"
    first_name = "Billy"
    last_name = "Bob"
    cid1 = 'facebook1'
    insert_vars = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'cid1': image_path
                   }

    html = """
    <header>
    </header>

    <body>
        <img src="cid:{cid1}" style="width: 30px;">
        <p> My first name is {first_name} and my
            last name is {last_name}.
        </p>

    </body>
    """

    send_mail(subject='Test email', to_emails=to_emails, from_email=username, text="see attached", html_file_path=html,
               html_inserts=insert_vars)

