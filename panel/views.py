from django.shortcuts import render, redirect
from django.forms import ValidationError
from panel.decorators import unAuthenticated_user
from django_countries import countries
from panel.models import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

@unAuthenticated_user
def loginApp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(home)
        else:
            return render(request, 'panel/login.html', {'message': 'Invalid credentials'})
    return render(request, 'panel/login.html')

@login_required(login_url='login')
def home(request):
    data = {}
    member = Member.objects.get(user = User.objects.get(id = request.user.id))
    activities = Activity.objects.filter(poster=member)
    data['activities'] = activities
    data['fullname'] = member.first_name + ' ' + member.last_name
    return render(request, 'panel/index.html', data)
    
@unAuthenticated_user
def signupApp(request):
    data = {}
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        country = request.POST.get('country')
        password = request.POST.get('password')
        conf_pass = request.POST.get('password_cnfrm')
        if firstname == '':
            data['error'] = 'Empty field (firstname) not permitted'
        if lastname == '':
            data['error'] = 'Empty field (lastname) not permitted'
        if email == '':
            data['error'] = 'Empty field (email) not permitted'
        if country == '':
            data['error'] = 'Empty field (country) not permitted'
        if 'error' in  data.keys():
            return render(request, 'panel/signup.html', data)
        # Set password
        if password != '' and conf_pass != '' and password == conf_pass:
            try:
                val = validate_password(password)
                if val == None:
                    user = User.objects.create_user(firstname[:10].lower(), email, password)
                    user.first_name = firstname
                    user.last_name = lastname
                    user.save()
                    st = Member.objects.create(
                        first_name = firstname,
                        last_name = lastname,
                        email = email,
                        user = user,
                        country = country,
                        balance = 1000000.00
                    )
                    st.save()
                    return redirect('home')
            except ValidationError as v:
                data['error'] = '\n'.join(v)
                return render(request, 'panel/signup.html', data)
    data['countries'] = dict(countries).values()
    return render(request, 'panel/signup.html', data)

def logoutApp(request):
    logout(request)
    return redirect(loginApp)