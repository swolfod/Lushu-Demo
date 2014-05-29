__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from django.core.urlresolvers import reverse
from Lushu.utils import *
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template import RequestContext, loader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def sendGmail(username, passwd, email, planDetail):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, passwd)

    template = loader.get_template('emailBody.html')
    context = RequestContext(request, {
        "dayPlans": planDetail
    })
    BODY = template.render(context)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header("Your Trip Plan".encode('utf-8'), 'UTF-8').encode()
    msg['To'] = Header(email.encode('utf-8'), 'UTF-8').encode()
    msg['From'] = Header(username.encode('utf-8'), 'UTF-8').encode()

    htmlpart = MIMEText(BODY.encode('utf-8'), 'html', 'UTF-8')
    msg.attach(htmlpart)
    #textpart = MIMEText(BODY.encode('utf-8'), 'html', 'UTF-8')
    #msg.attach(textpart)

    server.sendmail(username, [email], msg.as_string())
    server.quit()


def getPlan(request):
    planDetails = request.session.get("planDetails", None)

    if not planDetails:
        return HttpResponseRedirect(reverse("Lushu.views.detailPlanning"))

    invliadEmail = False
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            validate_email(email)
        except ValidationError as e:
            invliadEmail = True
        else:
            sendGmail("lushu.co@gmail.com", "roadbook", email, planDetails)
            return secureRender(request, "emailSent.html", {"hideFooter": True})


    return secureRender(request, "getPlan.html", {
        "dayPlans": planDetails,
        "lastPage": reverse("Lushu.views.detailPlanning"),
        "invliadEmail": invliadEmail,
        "finalStep": True
    })