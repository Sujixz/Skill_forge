from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Course,Profile, Lesson,Category, Enrollment,BillingDetails

User = get_user_model()


def index(request):
    courses = Course.objects.filter(is_published=True)
    enrollments = []
    categories = Category.objects.all()

    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(student=request.user)

    return render(request, 'index.html', {
        'courses': courses,
        'enrollments': enrollments,
        'categories': categories
    })


@login_required
def profile(request):
    profile,created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        phone = request.POST.get('phone')
        profile_image = request.FILES.get('profile_image')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.profile_image = profile_image
        
        user.save()

        profile.bio = bio
        profile.phone = phone
        if profile_image:
            profile.profile_image = profile_image
        profile.save()

        return redirect('profile')

    context = {
        'profile': profile
    }
    return render(request, 'profile.html', context)


def courses(request):
    all_courses = Course.objects.filter(is_published=True)
    return render(request, 'course_detail.html', {'course_detail': all_courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()

   
    all_courses = Course.objects.filter(is_published=True).exclude(id=course.id)

    return render(request, 'course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'courses': all_courses
    })


def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    
    lessons = Lesson.objects.filter(course=course).order_by('order')

    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons
    }
    return render(request, 'lesson_detail.html', context)



from django.views.decorators.http import require_POST

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    Enrollment.objects.get_or_create(student=request.user, course=course)
    
    return redirect('enrolled_courses')

@login_required
def enrolled_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'enrolled_courses.html', {'enrollments': enrollments})

@login_required
def course_content(request, course_id):
    enrollment = get_object_or_404(Enrollment, student=request.user, course_id=course_id)
    lessons = enrollment.course.lessons.all()
    return render(request, 'course_content.html', {'course': enrollment.course, 'lessons': lessons})

def aboutUs(request):
    return render(request, 'aboutUs.html')

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

def contactUs(request):
    success = False

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        subject = f"New Contact Message from {name}"
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        success = True

    return render(request, "contactUs.html", {"success": success})    





def signup(request):
    if request.method == "POST":
        print(request.method)
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        print(username,email,password1,password2)

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")
        
        elif username == password1:
            messages.error(request,"Username and Password must be different")
            return render(request,"signup.html")


        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")

        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("signin")

    return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

      

        try:
            user = User.objects.get(email=email)

            print(user)
            auth_user = authenticate(request, username=user.username, password=password)

            if auth_user:
                login(request, auth_user)
                messages.success(request, "Logged in successfully.")
                return redirect("index")
            else:
                messages.error(request, "Invalid credentials.")
                return render(request, "signin.html")

        except User.DoesNotExist:
            messages.error(request, "No user with this email found.")
            return render(request, "signin.html")

    return render(request, "signin.html")


def userlogout(request):
    logout(request)
    return redirect("index")

# forget password ( when user clicks on frget paasewrd)

import random
from django.core.mail import send_mail
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = random.randint(100000, 999999)
        request.session['otp'] = str(otp)
        request.session['email'] = email

        # Send OTP via email
        send_mail(
            'Your OTP for Password Reset',
            f'Your OTP is: {otp}',
            'your_email@gmail.com',
            [email],
            fail_silently=False,
        )

        return redirect('verify_otp')

    return render(request, 'forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            # OTP correct, redirect to index
            messages.success(request, "OTP Verified Successfully!")
            return redirect('index')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')

# Dashboard View - Show enrolled courses
@login_required
def dashboard(request):
    enrolled_courses = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'dashboard.html', {
        'user': request.user,
        'enrolled_courses': enrolled_courses,
    })

def checkout_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'checkout.html', {'course': course})





from django.conf import settings
import razorpay

def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        # Get billing form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip')

        # Save billing details
        billing = BillingDetails.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            zip_code=zip_code
        )

        
        request.session['billing_id'] = billing.id
        request.session['course_id'] = course.id
        request.session.modified = True

        return redirect(f'/checkout/{course_id}/?start_payment=true')

    # GET request - Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

    order_amount = int(course.price) * 100
    order_currency = 'INR'
    order_receipt = f'order_rcptid_{course.id}'

    order = client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt,
        'payment_capture': 1
    })

    context = {
        'course': course,
        'order_id': order['id'],
        'order_amount': order_amount,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }

    return render(request, 'checkout.html', context)




def payment(request):

    return redirect('payment_success')


from django.core.mail import send_mail
@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    course_id = request.session.get('course_id')
    billing_id = request.session.get('billing_id')

    print("PAYMENT ID:", payment_id)
    print("COURSE ID:", course_id)
    print("BILLING ID:", billing_id)

    course = Course.objects.get(id=course_id) if course_id else None
    billing = BillingDetails.objects.get(id=billing_id) if billing_id else None


    if course:
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        print("ENROLLMENT CREATED:", created)

    
    if billing and course:
        send_mail(
            subject=f'Payment Confirmation - {course.title}',
            message=f'''
Hello {billing.first_name} {billing.last_name},

Thank you for your payment!

 Payment ID: {payment_id}
 Course: {course.title}
 Amount Paid: ₹{course.price}

You can now access your course anytime by logging into your account.

Happy Learning!
Skill Forge Team
''',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[billing.email],
            fail_silently=False,
        )
        print("Confirmation email sent to:", billing.email)

    
    request.session.pop('course_id', None)
    request.session.pop('billing_id', None)

    context = {
        'payment_id': payment_id,
        'course': course,
        'billing': billing,
    }

    return render(request, 'payment_success.html', context)




def wishlist(request):
    return render(request, 'wishlist.html')

from .models import Category

def categories_processor(request):
    return {'categories': Category.objects.all()}

from django.db.models import Q

def search_results(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    courses = Course.objects.filter(is_published=True)
    

    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    if category_id:
        courses = courses.filter(category_id=category_id)

    categories = Category.objects.all()    

    context = {
        'query': query,
        'courses': courses,
        'categories': categories,
    }
    return render(request, 'search_results.html', context)

import random
from django.core.mail import send_mail

def request_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = str(random.randint(1000, 9999))

        try:
            user = User.objects.get(email=email)
            # Save OTP in session
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp

            # Send email
            send_mail(
                'Your OTP for Password Reset',
                f'Hello,\n\nYour OTP for password reset is: {otp}\n\nSkill Forge',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('reset_password')

        except User.DoesNotExist:
            return render(request, 'request_password.html', {'error': 'Email not found'})

    return render(request, 'request_password.html')


def reset_password(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        session_otp = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if not email or not session_otp:
            return redirect('request_password')  

        #  OTP verification
        if input_otp != session_otp:
            return render(request, 'reset_password.html', {'error': '❌ Invalid OTP entered.'})

       
        if new_password != confirm_password:
            return render(request, 'reset_password.html', {'error': '❌ Passwords do not match.'})

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            request.session.pop('reset_otp')
            request.session.pop('reset_email')

            return redirect('signin')  

        except User.DoesNotExist:
            return render(request, 'reset_password.html', {'error': 'User not found.'})

    return render(request, 'reset_password.html')






