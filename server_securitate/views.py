from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from .models import *
from datetime import datetime, timedelta, timezone, tzinfo
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from Crypto.PublicKey import RSA
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .rsa import *
import json
import requests
from django import forms
from .settings import RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY, EMAIL_HOST_USER
import cv2
import base64
import numpy as np
import threading
import random
from django.views.decorators import gzip
from .stream import Stream
from django.core.mail import send_mail
from .mail import *
from django.contrib.auth.hashers import make_password
from hashlib import sha256
from  django_recaptcha.fields import ReCaptchaField
from django.core.files.uploadedfile import UploadedFile 
import io
EMAIL_ADDR = EMAIL_HOST_USER


class FormWithCaptcha(forms.Form):
    captcha = ReCaptchaField()

tz = timezone(timedelta(hours=2))

streams = {}

@login_required(redirect_field_name=None)
def index(request):
    try:
        connections = Connections.objects.filter(user=request.user.username)
        uids = []
        if(connections is not None):
            for c in connections:
                print(c.uid)
                uids.append(c.uid)
        print(uids)
        
        p = PIR.objects.filter(value=1).order_by('uid').order_by('timestamp')
        u = USA.objects.order_by('uid').order_by('timestamp')
        d = DHT.objects.order_by('uid').order_by('timestamp')
        c = CAMERA.objects.order_by('uid').order_by('timestamp')

        pir = []
        usa = []
        dht = []
        cam = []
        for (l1, l) in [(p, pir), (u, usa), (d, dht), (c, cam)]:
            uid = ""
            for x in l1:
                print(x.uid)
                if uid != x.uid and x.uid in uids:
                    l.append(x)
                    uid = x.uid
        print(pir)
        print(usa)
        print(dht)
        print(cam)
        return render(request, 'index.html', {'pir':pir, 'usa':usa, 'dht':dht, 'cam':cam, "username":request.user.username})
        
    except (PIR.DoesNotExist, USA.DoesNotExist, DHT.DoesNotExist, CAMERA.DoesNotExist, Connections.DoesNotExist):
        return render(request, 'message.html', {'msg' : "A aparut o eroare"})


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        captcha = ReCaptchaField(
            public_key=RECAPTCHA_PUBLIC_KEY,
            private_key=RECAPTCHA_PRIVATE_KEY
        )
        
        
        user_object = User.objects.filter(username=username).last()
        if user_object is None:
            user_object = User.objects.filter(email=username).last()
            
        if user_object is None:
            return render(request, 'login.html', {'fail':True, 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
            
        if user_object.is_active == 0:
            send_mail(
                "Confirmare adresa email",  
                "",
                EMAIL_ADDR,
                [user_object.email],
                html_message=generate_mail_confirm(user_object.username, user_object.email))
            return render(request, 'message.html', {'msg' : "Adresa de email nu e confirmata, va rugam sa o confirmati"})
        
        
        
        user = authenticate(username=username, password=password)
        if user is None:
            try:
                user_object = User.objects.get(email=username.lower())
                username = user_object.username
            except User.DoesNotExist:
                return render(request, 'login.html', {'fail':True, 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
            user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'fail':True, 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
        
        user_object = User.objects.filter(username=username).last()
        if user_object.is_active == 0:
            send_mail(
                "Confirmare adresa email",  
                "",
                EMAIL_ADDR,
                [user_object.email],
                html_message=generate_mail_confirm(user_object.username, user_object.email))
            return render(request, 'message.html', {'msg' : "Adresa de email nu e confirmata, va rugam sa o confirmati"})
        login(request, user)
        return redirect('/')
    return render(request, 'login.html', {'fail':False, 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})



@login_required
def settings_page(request):
    return render(request, 'settings.html', {'email':request.user.email, "username":request.user.username})


@login_required
def add_device(request):
    uid = request.GET.get("uid")
    print(uid)
    if uid is not None:
        try:
            conn = Connections.objects.filter(uid=uid)
            if conn is None:
                c = Connections(uid=uid, user=request.user.username)
                c.save()
                return HttpResponse("@success")
            else:
                for c in conn:
                    if request.user.username == c.user:
                        return HttpResponse("eroare")
            for c in conn:
                try:
                    user_object = User.objects.filter(username=c.user).last()
                    if user_object is None:
                        continue
                    send_mail(
                        "Cerere adaugare dispozitiv",
                        "",
                        EMAIL_ADDR,
                        [user_object.email],
                        html_message=generate_mail_add(uid, c.user, request.user.username))
                except User.DoesNotExist:
                    pass
            return HttpResponse("@mail")
        except ( Connections.DoesNotExist):
            return HttpResponse("eroare")
    return HttpResponse("eroare")

@login_required
def delete_device(request):
    uid = request.GET.get("uid")
    type = request.GET.get("type")
    if uid is not None and type is not None:
        uid = int(uid)
        try:
            ok = False
            conn = Connections.objects.filter(uid=uid).filter(user=request.user.username)
            if conn is not None:
                ok = True
                conn.delete()            

            if ok:
                return HttpResponse("@success")
        except (Connections.DoesNotExist):
            return HttpResponse("eroare")
    return HttpResponse("eroare")


@csrf_exempt
def devices(request):
    payload = request.POST.get("payload")
    data = rsa_decrypt(payload)
    
		
    try:
        print(request_get(data, 'type'))
        if request_get(data, 'type') == 'PIR':

            mac = request_get(data, 'mac')
            value = int(request_get(data, 'value'))
            uid = request_get(data, 'uid')
            timestamp = datetime.now(tz)

            pir = PIR(mac=mac, value=value, timestamp=timestamp, uid=uid)
            print(mac)
            print(value)
            print(uid)
            pir.save()
        elif request_get(data, 'type') == 'USA':
            mac = request_get(data, 'mac')
            value = int(request_get(data, 'value'))
            timestamp = datetime.now(tz)
            uid = request_get(data, 'uid')
            
            usa = USA(mac=mac, value=value, timestamp=timestamp, uid=uid)
            usa.save()
        elif request_get(data, 'type') == 'DHT':
            mac = request_get(data, 'mac')
            temperature = float(request_get(data, 'temp'))
            humidity = float(request_get(data, 'hum'))
            timestamp = datetime.now(tz)
            uid = request_get(data, 'uid')
            
            dht = DHT(mac=mac, temperature=temperature, humidity=humidity, timestamp=timestamp,  uid=uid)
            dht.save()
        elif request_get(data, 'type') == 'CAMERA':
            uid = request_get(data, "uid")

            conn = Connections.objects.filter(uid=uid).last()
            if conn is None:
                return HttpResponse("eroare")
            user = User.objects.filter(username=conn.user).last()
            if user is None:
                return HttpResponse("eroare")
            email = user.email

            image = request.POST.get("image")
            image=base64.b64decode(image)
            #print(image)
            #image=image[:-1]
            send_mail_movement(
                "A fost detectata miscare!",
                "",
                EMAIL_ADDR,
                [email],
                image
            )
            image = UploadedFile(file=io.BytesIO(image), name="image.jpg", size=len(image), content_type="image/jpeg", charset=None)
            img = ImageHistory(uid=uid, image=image, timestamp=datetime.now(tz))
            img.save()		
        #print(request.POST)
            
    except (PIR.DoesNotExist, USA.DoesNotExist, DHT.DoesNotExist, CAMERA.DoesNotExist):
        return HttpResponse("eroare")
    
    return HttpResponse("ok")

def send_public_key(request):
    f = open("rsa_public_key.pem", "r")
    content = f.read()
    f.close()
    response     = HttpResponse(content,'application/pem-certificate-chain')
    response['Content-Length']      = len(content)
    response['Content-Disposition'] = 'attachment; filename="rsa_public_key.pem"'
    return response
    

@login_required
def data(request):
    n = request.GET.get("n")
    if n is None:
        return HttpResponse("{}")
    n = int(n)
    d = {}
    arr = []
    for i in range(1, n+1):
        uid = request.GET.get("uid" + str(i))
        type = request.GET.get("type" + str(i))
        if uid is None or type is None:
            return HttpResponse("{}")
        obj = None
        try:
            conn = Connections.objects.filter(uid=uid).filter(user=request.user.username)
            if conn is None:
                raise Exception
            
            if type == "PIR":
                obj = PIR.objects.filter(uid=uid).filter(value=1).last()
            if type == "USA":
                obj = USA.objects.filter(uid=uid).last()
            if type == "DHT":
                obj = DHT.objects.filter(uid=uid).last()
            if type == "CAMERA":
                obj = CAMERA.objects.filter(uid=uid).last()
        except (PIR.DoesNotExist, USA.DoesNotExist, DHT.DoesNotExist, CAMERA.DoesNotExist, Connections.DoesNotExist, Exception):
            pass
        if obj is None:
            return HttpResponse("{}")
        
        d1 = {}
        t = obj.timestamp.strftime('%H:%M %d.%m.%Y')
        d1["name"] = obj.name
        d1["mac"] = obj.mac
        d1["timestamp"] = t
        if type == "PIR" or type == "USA":
            d1["value"] = str(obj.value)
        elif type == "DHT":
            d1["temperature"] =  str(obj.temperature) 
            d1["humidity"] = str(obj.humidity)
        
        arr.append(d1)
    d["data"] = arr
    return HttpResponse(json.dumps(d))
    

@login_required
def edit_name(request):
    uid = request.GET.get("uid")
    type = request.GET.get("type")
    name = request.GET.get("name")
    if uid is None or type is None or name is None:
        return HttpResponse("err")
    obj = None
    try:
        conn = Connections.objects.filter(uid=uid).filter(user=request.user.username)
        if conn is None:
            raise Exception
        if type == "CAMERA":
            obj = CAMERA.objects.filter(uid=uid)
        if type == "PIR":
            obj = PIR.objects.filter(uid=uid)
        if type == "USA":
            obj = USA.objects.filter(uid=uid)
        if type == "DHT":
            obj = DHT.objects.filter(uid=uid)
    except (PIR.DoesNotExist, USA.DoesNotExist, DHT.DoesNotExist, CAMERA.DoesNotExist, Connections.DoesNotExist, Exception):
        pass

    if obj is None:
        return HttpResponse("err")
    
    for o in obj:
        o.name = name
        o.save()

    return HttpResponse("@success")

@csrf_exempt
def request_uid(request):
    payload = request.POST.get("payload")
    
    data = rsa_decrypt(payload)
    
    username = request_get(data, 'username')
    password = request_get(data, 'password')
    mac = request_get(data, 'mac')
    tip = request_get(data, 'type')
    
    user = authenticate(username=username, password=password)
    if user is None:
        try:
            user_object = User.objects.get(email=username.lower())
            username = user_object.username
        except User.DoesNotExist:
            return HttpResponse("err")
        user = authenticate(username=username, password=password)

    if user is None:
            return HttpResponse("err")
    
    import random
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars=[]
    for i in range(12):
        chars.append(random.choice(ALPHABET))
    chars = ''.join(chars)
    
    uid = UID(mac=mac, type=tip, uid=chars)
    uid.save()
    c = Connections(user=username, uid=uid.uid)
    c.save()
    
    if tip == "DHT":
        dht = DHT(mac=mac, timestamp=datetime.now(tz), uid=uid.uid)
        dht.save()
    if tip == "USA":
        usa = USA(mac=mac, timestamp=datetime.now(tz), uid=uid.uid)
        usa.save()
    if tip == "PIR":
        pir = PIR(mac=mac, timestamp=datetime.now(tz), uid=uid.uid)
        pir.save()
    if tip == "CAMERA":
        cam = CAMERA(mac=mac, timestamp=datetime.now(tz), uid=uid.uid)
        cam.save()
    
    print(uid.uid)
    return HttpResponse(str(uid.uid))


def http_post(capcha, key):
    url = 'https://www.google.com/recaptcha/api/siteverify?secret=' + key
    url = url + "&response="+capcha
    dict = {}
    x = requests.post(url, json=dict)
    print(x.text)
    j = json.loads(x.text)
    if j["success"] == True:
        return j["score"]
    return 0
    
def port(request):
    uid = request.GET.get('uid')
    cam = None
    try:
        cam = CAMERA.objects.filter(uid=uid).last()
    except (CAMERA.DoesNotExist):
        print("does not exist")
        return HttpResponse("0")
    if cam is None:
        print("is none")
        return HttpResponse("0")
    
    t = datetime.now(tz)
    time_diff = t - cam.timestamp
    
    if time_diff.total_seconds() > 70:
        cam.socket = 0
        cam.save()
        if uid in streams:
            streams[uid].stop_stream()
            streams.pop(uid, None)
    
    return HttpResponse(str(cam.socket))
    

@login_required
def start_stream(request):
    status = request.GET.get('status')
    uid = request.GET.get('uid')
    if status is None or uid is None:
        return HttpResponse("0")
    status = int(status)
    
    cam = None
    try:
        conn = Connections.objects.filter(uid=uid).filter(user=request.user.username)
        if conn is None:
            raise Exception
        cam = CAMERA.objects.filter(uid=uid).last()
    except (CAMERA.DoesNotExist, Connections.DoesNotExist, Exception):
        return HttpResponse("0")
    if cam is None:
        print("nu e camera")
        return HttpResponse("0")
        
    if status == 1:
        cam.timestamp = datetime.now(tz)
        if cam.socket == 0:
            r = random.randint(59000, 65500)
            
            while True:
                try:
                    cam1 = CAMERA.objects.filter(socket=r).last()
                    if cam1 is None:
                        break
                except (CAMERA.DoesNotExist):
                    break
            
            cam.socket = r
            obj = Stream(r, uid)
            streams[uid] = obj
            obj.start_stream()
    else:
        cam.timestamp = datetime.now(tz)
        cam.socket = 0
        if uid in streams:
            streams[uid].stop_stream()
            streams.pop(uid, None)
    cam.save()
    return HttpResponse(str(cam.socket))

@gzip.gzip_page
@login_required
def livefeed(request):
    uid = request.GET.get("uid")
    if(uid is None):
        return HttpResponse("")

    if uid not in streams:
        return HttpResponse("")
        
    try:
        conn = Connections.objects.filter(uid=uid).filter(user=request.user.username)
        if conn is None:
            raise Exception
        cam = CAMERA.objects.filter(uid=uid).last()
    except (CAMERA.DoesNotExist, Exception):
        return HttpResponse("")
    if cam is None:
        return HttpResponse("")

    try:
        cam = streams[uid]
        print("aaa")
        return HttpResponse(cam.get_image(), content_type="image/jpeg")
        #return StreamingHttpResponse(cam.gen(), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        return HttpResponse("")
    
def check_credentials(request):
    time.sleep(0.5)

    username = request.GET['username']
    password = request.GET['password']
    
    user = authenticate(username=username, password=password)
    if user is None:
        try:
            user_object = User.objects.get(email=username.lower())
            username = user_object.username
        except User.DoesNotExist:
            return HttpResponse("err")
        user = authenticate(username=username, password=password)

    if user is None:
        return HttpResponse("err")

    return HttpResponse("@success")
    

@login_required
def request_add(request):
    t = datetime.now(tz)
    user1 = request.GET.get('user')
    user = request.user.username
    if user != user1:
        return render(request, 'message.html', {'msg' : "Utilizatorul nu are drepturi de adaugare"})
    
    from_user = request.GET.get('from_user')
    uid = request.GET.get('uid')
    
    if from_user is None or uid is None:
        return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
        
    try:
        r = Requests.objects.filter(user=user).filter(uid=uid).filter(from_user=from_user).last()
        if r is None:
            return render(request, 'message.html', {'msg' : "Utilizatorul nu are drepturi de adaugare"})
        duration = t - r.timestamp
        if duration.total_seconds() > 24 * 60 * 60:
            return render(request, 'message.html', {'msg' : "Linkul accesat a expirat"})
        c = Connections(uid=r.uid, user=from_user)
        r = Requests.objects.filter(uid=uid).filter(from_user=from_user)
        c.save()
        for i in r:
            i.delete()
        return render(request, 'message.html', {'msg' : "Dispozitivul a fost adaugat cu succes"})
    except:
        return render(request, 'message.html', {'msg' : "A aparut o eroare in procesarea datelor"})
    
def confirm_email(request):
    t = datetime.now(tz)
    user = request.GET.get('user')
    email = request.GET.get('email')
    
    if user is None or email is None:
        return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
        
    try:
        u = User.objects.filter(username=user).last()
        u.is_active = 1
        u.save()
        
        return render(request, 'message.html', {'msg' : "Adresa de email a fost confirmata cu succes"})
    except (User.DoesNotExist):
        return render(request, 'message.html', {'msg' : "A aparut o eroare in procesarea datelor"})
    
    
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        
        captcha = ReCaptchaField(
            public_key=RECAPTCHA_PUBLIC_KEY,
            private_key=RECAPTCHA_PRIVATE_KEY
        )
        if password != password1:   
            return render(request, 'signup.html', {'fail':True, 'msg' : 'Parolele nu sunt identice!', 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
        
        try:
            u = User.objects.filter(username=username).last()
            u1 = User.objects.filter(email=email).last()
            if u is not None:
                return render(request, 'signup.html', {'fail':True, 'msg' : 'Utilizatorul exista deja!', 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
            if u1 is not None:
                return render(request, 'signup.html', {'fail':True, 'msg' : 'Adresa de email este deja folosita!', 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
        except:
            pass
            
        import random
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars=[]
        for i in range(16):
            chars.append(random.choice(ALPHABET))
        
        
        hashed_pass =  make_password(password, salt=''.join(chars), hasher='default')
            
        user_object = User(is_active=0, email=email, username=username, password=hashed_pass)
        user_object.save()
        
        send_mail(
            "Confirmare adresa email",
            "",
            EMAIL_ADDR,
            [user_object.email],
            html_message=generate_mail_confirm(user_object.username, user_object.email))
        #TODO
        return render(request, 'message.html', {'msg' : "Confirmati adresa de email"})
            
    return render(request, 'signup.html', {'fail':False, 'msg' : '', 'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})


def forgot_password(request):
    if request.method == "GET":
        email = request.GET.get('email')
    else:
        email = request.POST.get('email')
    if email is not None:
        captcha = ReCaptchaField(
            public_key=RECAPTCHA_PUBLIC_KEY,
            private_key=RECAPTCHA_PRIVATE_KEY
        )
        
        try:
            user = User.objects.filter(email=email.lower()).last()

            if user is not None:
                import random
                ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                chars=[]
                for i in range(16):
                    chars.append(random.choice(ALPHABET))
                chars = ''.join(chars)
                key=sha256(chars.encode('ascii')).hexdigest()
                entry = ResetPassword(email=email, key=key)
                entry.save()
                send_mail(
                    "Resetare parola",
                    "",
                    EMAIL_ADDR,
                    [email],
                    html_message=generate_mail_forgot_password(email, chars))
                return render(request, 'message.html', {'msg' : "Succes! Verificati adresa email"})
        except:
            pass
        
        
        return render(request, 'message.html', {'msg' : "Succes! Verificati adresa email"})
    else:
        return render(request, 'forgot_password.html', {'PUBLIC_KEY' : RECAPTCHA_PUBLIC_KEY})
    
def forgot_password_link(request):
    email=request.GET.get('email')
    key=request.GET.get('key')
    if email is None or key is None:
        email=request.POST.get('email')
        key=request.POST.get('key')
    if email is None or key is None:
        return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
    try:
        
        r = ResetPassword.objects.filter(email=email, key=sha256(key.encode('ascii')).hexdigest()).last()
        if r is not None:
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')
            
            if pass1 is None:
                return render(request, 'forgot_password_link.html', {'fail':False, 'reason' : '', 'email':email, 'key':key})
            if pass1 != pass2:
                return render(request, 'forgot_password_link.html', {'fail':True, 'reason' : 'Parolele nu coincid', 'email':email, 'key':key})
            if len(pass1) < 8:
                return render(request, 'forgot_password_link.html', {'fail':True, 'reason' : 'Parola nu este suficient de lunga', 'email':email, 'key':key})
            
            import random
            ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            chars=[]
            for i in range(16):
                chars.append(random.choice(ALPHABET))
        
            hashed_pass =  make_password(pass1, salt=''.join(chars), hasher='default')
            user_object = User.objects.filter(email=email).last()
            if user_object is None:
                return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
            user_object.password=hashed_pass
            user_object.save()
            r.delete()
            return render(request, 'message.html', {'msg' : "Parola a fost resetata cu succes!"})
        print("none")
            
    except Exception as e:
        return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
    return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
    
@login_required
def camera(request):
    try:
        connections = Connections.objects.filter(user=request.user.username)
        camera = []
        if(connections is not None):
            for c in connections:
                cam = CAMERA.objects.filter(uid=c.uid).last()
                if cam is not None:
                    camera.append(cam)
        #camera.append(CAMERA(uid="23", name="camera5"))
        return render(request, 'camera.html', {"camera":camera, "username":request.user.username})
    except:
        return render(request, 'message.html', {'msg' : "A aparut o eroare"})
    

@login_required
def profile(request):
    return render(request, 'profile.html', {"username":request.user.username})
    
@login_required
def change_email(request):
    email = request.GET.get("email")
    print(email)
    import re
    pattern = "^[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*$"
    if re.search(pattern, email) is not None:
        print("pattern ok")
        user = User.objects.filter(username=request.user.username).last()
        if user is not None:
            print("user ok")
            user.email=email
            user.is_active=0
            user.save()
            
            send_mail(
                "Confirmare adresa email",
                "",
                EMAIL_ADDR,
                [email],
                html_message=generate_mail_confirm(user.username, email))
            
            return render(request, 'message.html', {'msg' : "Adresa de email a fost modificata cu succes! Nu uitati sa confirmati noua adresa de email"})
    return render(request, 'message.html', {'msg' : "Linkul accesat este invalid"})
    
    
@login_required
def delete_account(request):
    user = request.user.username
    try:
        conns = Connections.objects.filter(user=user)
        print("aici")
        device_ids = []
        if conns is not None:
        
            for c in conns:
                device_ids.append(c.uid)
                c.delete()
            for i in device_ids:
                conns = Connections.objects.filter(uid=i)
                if conns is None:
                    for DEV in [PIR, USA, CAMERA, DHT]:
                        dev = DEV.objects.filter(uid=i)
                        if dev is not None:
                            for d in dev:
                                d.delete()
        user = User.objects.filter(username=user).last()
        email = user.email
        res = ResetPassword.objects.filter(email=email)
        if res is not None:
            for r in res:
                r.delete()
        res = Requests.objects.filter(user=user)
        if res is not None:
            for r in res:
                r.delete()
        res = Requests.objects.filter(from_user=user)
        if res is not None:
            for r in res:
                r.delete()
        user.delete()
    except:
        print("except")
        return render(request, 'message.html', {'msg' : "A aparut o eroare"})
                
    return render(request, 'message.html', {'msg' : "Contul a fost sters cu succes!"})
@login_required
def image_history(request):
    from django_user_agents.utils import get_user_agent
    user_agent = get_user_agent(request)
    conns = Connections.objects.filter(user=request.user.username)
    if conns is None:
        return HttpResponse("err")

    images = []
    for conn in conns:
        imgs = ImageHistory.objects.filter(uid=conn.uid)
        if imgs is not None:
            for img in imgs:
                images.append(img)
    print(len(images))
    return render(request, 'image_history.html', {'telefon': user_agent.is_mobile, 'images': images, 'N':len(images)})