import requests
import json

def mail_camera_status(text):
    url = "https://a8mailer.herokuapp.com/v1/mailer"

    payload = json.dumps({
      "userFrom": "jitender.thakur@algo8.ai",
      "userPass": "Jit_algo={10}",
      "toEmail": "pramod.jangid@algo8.ai,Pratyush.Panda@vedanta.co.in,Himmat.Hadiya@vedanta.co.in,Manoj.Jain@vedanta.co.in,karun.jain@vedanta.co.in",
      "subjectOfMail": "camera status",
      "textOfMail": "",
      "htmlOfMail": "<html><head></head><body> <p style='color:blue'> {}</p></body></html>".format(text)
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    