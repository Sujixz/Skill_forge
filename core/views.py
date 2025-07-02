from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Enrollment,BillingDetails

User = get_user_model()


def index(request):
    courses = Course.objects.filter(is_published=True)
    enrollments = []

    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(student=request.user)

    return render(request, 'index.html', {
        'courses': courses,
        'enrollments': enrollments
    })


def courses(request):
    all_courses = Course.objects.filter(is_published=True)
    return render(request, 'course_detail.html', {'course_detail': all_courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()

    # Exclude current course from related list
    all_courses = Course.objects.filter(is_published=True).exclude(id=course.id)

    return render(request, 'course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'courses': all_courses
    })


from django.views.decorators.http import require_POST

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Payment verification logic should be implemented here
    # For now, assuming payment is successful as this is called after checkout
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




# from django.shortcuts import render, redirect, get_object_or_404
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

        # Save IDs in session for payment_success retrieval
        request.session['billing_id'] = billing.id
        request.session['course_id'] = course.id
        request.session.modified = True

        # Redirect to same page with ?start_payment=true to trigger Razorpay
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

    # Save
    if course:
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        print("ENROLLMENT CREATED:", created)

    context = {
        'payment_id': payment_id,
        'course': course,
        'billing': billing,
    }

    
    request.session.pop('course_id', None)
    request.session.pop('billing_id', None)

    return render(request, 'payment_success.html', context)



def wishlist(request):
    return render(request, 'wishlist.html')


from django.db.models import Q

def search_results(request):
    query = request.GET.get('q', '').strip()
    courses = []

    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'courses': courses
    }
    return render(request, 'search_results.html', context)



