from .models import *
from .settings import IP
from datetime import datetime, timedelta, timezone, tzinfo
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

tz = timezone(timedelta(hours=2))

def name_by_id(uid):
    try:
        p = PIR.objects.filter(uid=uid).last()
        u = USA.objects.filter(uid=uid).last()
        d = DHT.objects.filter(uid=uid).last()
        c = CAMERA.objects.filter(uid=uid).last()
        if p is not None:
            return p.name
        if u is not None:
            return u.name
        if d is not None:
            return d.name
        if c is not None:
            return c.name
        return ""
    except (PIR.DoesNotExist, USA.DoesNotExist, DHT.DoesNotExist, CAMERA.DoesNotExist, Connections.DoesNotExist):
        return ""

def generate_mail_add(uid, user, from_user):
	r = Requests(uid=uid, user=user, from_user=from_user, timestamp=datetime.now(tz))
	r.save()
	nume_dispozitiv = name_by_id(uid)
	s= "<html>"
	s += "<head></head>"#TODO
	s += "<body>"
	s += "<h1> Utilizatorul " + from_user + " a cerut adaugarea dispozitivului " + nume_dispozitiv + "</h1>"
	s += "<h2> Apasati pe butonul de mai jos pentru a accepta cererea</h2>"
	s += "<button><a href='"
	s += "http://"+IP+"/request_add/?uid=" + uid + "&user=" + user + "&from_user=" + from_user
	s += "'>Acceptati</a></button>"
	s += "</body>"
	s +="</html>"
	
	return s
	
def generate_mail_confirm(user, email):
	s= "<html>"
	s += "<head></head>"#TODO
	s += "<body>"
	s += "<h1> Va rugam sa confirmati adresa de email:" + email + "</h1>"
	s += "<h2> Apasati pe butonul de mai jos pentru a confirma</h2>"
	s += "<button><a href='"
	s += "http://"+IP+"/confirm_email/?email=" + email + "&user=" + user
	s += "'>Confirm</a></button>"
	s += "</body>"
	s +="</html>"
	return s
	
def generate_mail_forgot_password( email, key):
	s= "<html>"
	s += "<head></head>"#TODO
	s += "<body>"
	s += "<h1> Resetare parola</h1>"
	s += "<h2> Va rugam accesati urmatorul link pentru a reseta parola</h2>"
	s += "<button><a href='"
	s += "http://"+IP+"/forgot_password_link?email="+email+"&key="+key 
	s += "'>Confirm</a></button>"
	s += "</body>"
	s +="</html>"
	return s

def send_mail_movement(subject, body, from_email, to_email_list, image_data):
	message = EmailMultiAlternatives(
		subject=subject,
		body=body,
		from_email=from_email,
		to=to_email_list
	)
	s= "<html>"
	s += "<head></head>"
	s += "<body>"
	s += "<h1> A fost detectata miscare</h1>"
	s += "<img heigth=600 src='cid:image1.jpg'>"
	s += "</img>"
	s += "</body>"
	s +="</html>"
	message.mixed_subtype = 'related'
	message.attach_alternative(s, "text/html")
	image = MIMEImage(image_data,_subtype="jpg")
    
	image.add_header('Content-ID', '<image1.jpg>')
	message.attach(image)
	message.send()