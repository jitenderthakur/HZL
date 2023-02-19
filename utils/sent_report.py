import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
smtp_server = 'smtp-mail.outlook.com'
smtp_port = 587
gmail = 'mukesh.kumar@algo8.ai'
password = 'mukesh123@algo8'
message = MIMEMultipart('mixed')
message['From'] = 'Contact <{sender}>'.format(sender = gmail)
def sendReport(subject,msgContent,attachedFile,to,cc):
    message['To'] = to
    message['Subject'] = subject
    msg_content = '{}\n'.format(msgContent)
    body = MIMEText(msg_content, 'html')
    message.attach(body)
    attachmentPath = attachedFile
    try:
        with open(attachmentPath, "rb") as attachment:
            p = MIMEApplication(attachment.read(),_subtype="pdf")   
            p.add_header('Content-Disposition', "attachment; filename= %s" % attachmentPath.split("\\")[-1]) 
            message.attach(p)
    except Exception as e:
        print(str(e))
    msg_full = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(gmail, password)
        server.sendmail(gmail, to.split(";") + (cc.split(";") if cc else []),
                    msg_full)
        server.quit()
        return "email sent out successfully"
#print(sendReport("subject","HZL_PDF_REPORT","2022-04-04A.pdf","jitender.thakur@algo8.ai",""))
