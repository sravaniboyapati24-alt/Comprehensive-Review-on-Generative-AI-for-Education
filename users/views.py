
from django.shortcuts import render

from users.forms import  UserRegistrationForm
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import UserRegistrationModel
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserRegistrationModel


def base(request):
    return render(request,'base.html')



def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered') 
            return render(request,'UserRegistration.html')
        else:
            messages.error(request, 'Email or Mobile Already Exists')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistration.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('password')  # Corrected key to match the form input name
        try:
            user = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if user.status == "activated":
                request.session['id'] = user.id
                request.session['loggeduser'] = user.name
                return redirect('UserHome')  # Redirect to User Home after successful login
            else:
                messages.error(request, 'Your account is not activated.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password')
    return render(request, 'UserLogin.html')  # Ensure this is the correct template name


def UserHome(request):
    return render(request, 'users/UserHome.html')





# import os
# from django.shortcuts import render
# from dotenv import load_dotenv
# import google.generativeai as genai

# # Load environment variables (e.g., from .env)
# load_dotenv()

# # Configure Gemini API
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyAysVqWZ-Ydq8NTcPZN6QwpVX5JkEDE17Q"))

# # Use Gemini 2.0 Flash or Pro
# model = genai.GenerativeModel("models/gemini-2.0-flash")

# def generative_chat_view(request):
#     response_text = ""
#     user_input = ""

#     if request.method == "POST":
#         user_input = request.POST.get("message", "").strip()

#         if user_input:
#             try:
#                 prompt = f"You are a helpful assistant. Respond clearly.\n\nUser: {user_input}"
#                 response = model.generate_content(prompt)
#                 response_text = response.text.strip()
#             except Exception as e:
#                 response_text = f"⚠️ Error: {str(e)}"
#         else:
#             response_text = "⚠️ Please enter a message."

#     return render(request, "users/generate.html", {
#         "user_input": user_input,
#         "response_text": response_text,
#     })









import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyAysVqWZ-Ydq8NTcPZN6QwpVX5JkEDE17Q"))

# Use Gemini 2.0 Flash or Pro
model = genai.GenerativeModel("models/gemini-2.0-flash")



# Function to generate structured visual content
def generate_content(topic, role):
    prompt = f"""
    Generate structured, visual, and engaging learning content for a {role} on the topic '{topic}' using Generative AI.

    Requirements:
    - Provide rich explanations using headings and bullet points.
    - Include at least one diagram using a real image URL or base64 image.
    - Do NOT use [Placeholder for Image URL] or similar.
    - Embed diagrams directly using <img src="..."> for HTML rendering.
    - Avoid Mermaid, PlantUML, or text-based diagrams.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"<p style='color:red;'>Error generating content: {str(e)}</p>"

# Homepage view for form input and rendering
def home(request):
    result = ""
    topic = ""
    role = ""

    if request.method == 'POST':
        topic = request.POST.get('topic')
        role = request.POST.get('role')
        result = generate_content(topic, role)

        print(result)

    return render(request, 'users/generate.html', {
        'result': result,
        'topic': topic,
        'role': role
    })

# View to download content as PDF
def download_pdf(request):
    result = request.GET.get('result', '')
    topic = request.GET.get('topic', '')
    role = request.GET.get('role', '')

    template_path = 'users/pdf_template.html'
    context = {'result': result, 'topic': topic, 'role': role}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="GenAI_Education_Content.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed. Please try again.')

    return response
