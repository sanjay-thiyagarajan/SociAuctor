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
    deals = Deal.objects.filter(poster=member)
    data['activities'] = activities
    data['deals'] = deals
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

@login_required(login_url='login')
def add_deal(request):
    data = {}
    member = Member.objects.get(user = User.objects.get(id = request.user.id))
    if request.method == 'POST':
        title = request.POST.get('title')
        initial_price = request.POST.get('initial_price')
        activity = request.POST.get('activity')
        activity_id = activity.split(' - ')[0]
        deadline = request.POST.get('deadline')
        
        deal = Deal(
            title=title,
            poster=member,
            initial_price=initial_price,
            bid_price=initial_price,
            highest_bidder=member,
            activity=Activity.objects.get(id=activity_id),
            deadline=deadline,
            status='available'
            )
        deal.save()
        return redirect('home')
    activities = Activity.objects.filter(status='in-need')
    data['activities'] = activities
    data['fullname'] = member.first_name + ' ' + member.last_name
    return render(request, 'panel/add-deal.html', data)
    
@login_required(login_url='login')
def add_activity(request):
    data = {}
    try:
        member = Member.objects.get(user = User.objects.get(id = request.user.id))
    except:
        logoutApp(request)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        image = request.FILES.get('image')
        proofdoc = request.FILES.get('proofdoc')
        category = request.POST.get('category')
        deadline = request.POST.get('deadline')
        
        Activity.objects.create(
            title=title,
            poster=member,
            amount=amount,
            description=description,
            proof=proofdoc,
            deadline=deadline,
            status='in-need',
            category=Category.objects.get(name=category),
            image=image
        )
        return redirect('home')
    categories = Category.objects.all()
    data['categories'] = categories
    data['fullname'] = member.first_name + ' ' + member.last_name
    return render(request, 'panel/add-activity.html', data)

@login_required(login_url='login')
def view_activity(request, id):
    member = Member.objects.get(user = User.objects.get(id = request.user.id))
    activity = Activity.objects.get(id = id)
    poster = False
    if activity.poster.id == member.id:
        poster = True
    donated_amount = activity.donated_amount
    total = activity.amount
    percentage =  int((donated_amount / total ) * 100)
    remaining = total - donated_amount
    if request.method == 'POST':
        donation_amount = request.POST.get('donation_amount_field')
        if donation_amount > member.balance:
            return render(request, 'panel/view-activity.html', { 'error': 'Insufficient balance in your wallet.' })
        elif donation_amount > remaining:
            return render(request, 'panel/view-activity.html', { 'warning': 'We appreciate your kind gesture. But the provided amount exceeds the expected amount. We recommend you to donate through our product deal auctions to reward the extra amount to passionate dealers' })
        else:
            makeDonation(member, donation_amount, activity)
            return render(request, 'panel/view-activity.html', {'success': True})
    return render(request, 'panel/view-activity.html', { 'activity': activity, 'percentage': percentage, 'remaining': remaining, 'poster': poster })
    
@login_required(login_url='login')
def view_deal(request, id):
    member = Member.objects.get(user = User.objects.get(id = request.user.id))
    return render(request, 'panel/view-deal.html')

@login_required(login_url='login')
def wallet_view(request):
    member = Member.objects.get(user = User.objects.get(id = request.user.id))
    transactions = Transaction.objects.filter(payer = member)
    fullname = member.first_name + ' ' + member.last_name
    return render(request, 'panel/wallet-view.html', {'member' :member, 'fullname': fullname, 'transactions': transactions})

def logoutApp(request):
    logout(request)
    return redirect(loginApp)
    
def makeDonation(payer, amount, activity=None, deal=None):
    if activity is not None:
        activity.donated_amount += amount
        activity.poster.balance += amount
        payer.balance -= amount
        if activity.amount == activity.donated_amount:
            activity.status = 'achieved'
        activity.poster.save()
        activity.save()
        payer.save()
        tr = Transaction(
            payer=payer,
            amount=amount,
            activity=activity
        )
        tr.save()
    if deal is not None:
        donatable = deal.activity.amount - deal.activity.donated_amount
        deal.activity.donated_amount += donatable
        payer.balance -= donatable
        if deal.activity.donated_amount == deal.activity.amount:
            deal.activity.status = 'achieved'
        deal.activity.save()
        dealer_bonus = amount - donatable
        if dealer_bonus > 0:
            deal.poster.balance += dealer_bonus
            payer.balance -= dealer_bonus
            payer.save()
            deal.poster.save()
        deal.save()
        
        
        