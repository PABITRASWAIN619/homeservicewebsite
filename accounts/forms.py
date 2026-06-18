from django import forms
from datetime import date
from .models import WorkerProfile


# ==========================================
# WORKER SIGNUP FORM
# ==========================================

class WorkerSignupForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control"
        })
    )

    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )

    service_type = forms.ChoiceField(
        choices=WorkerProfile.SERVICE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3
        })
    )

    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    experience = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(
                "Passwords do not match"
            )

        dob = cleaned_data.get("date_of_birth")

        if dob:
            today = date.today()

            age = (
                today.year - dob.year
                - (
                    (today.month, today.day)
                    < (dob.month, dob.day)
                )
            )

            if age < 18:
                raise forms.ValidationError(
                    "Worker must be at least 18 years old"
                )

        return cleaned_data


# ==========================================
# CUSTOMER SIGNUP FORM
# ==========================================

class CustomerSignupForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Email"
        })
    )

    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Phone Number"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password"
        })
    )

    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(
                "Passwords do not match"
            )

        return cleaned_data


# ==========================================
# LOGIN FORM
# ==========================================

class LoginForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )
    from django import forms
from datetime import date

# =========================
# STEP 1
# =========================
class WorkerStep1Form(forms.Form):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 18 or age > 60:
            raise forms.ValidationError("Worker must be 18–60 years old")

        return dob


# =========================
# STEP 2
# =========================
class WorkerStep2Form(forms.Form):
    service_type = forms.ChoiceField(choices=[
        ('Electrician', 'Electrician'),
        ('Plumber', 'Plumber'),
        ('AC Repair', 'AC Repair'),
        ('Mobile Repair', 'Mobile Repair'),
        ('Carpenter', 'Carpenter'),
        ('Painter', 'Painter'),
        ('Cleaning Service', 'Cleaning Service'),
    ])

    address = forms.CharField(widget=forms.Textarea)
    pincode = forms.CharField(max_length=10)
    experience = forms.CharField(max_length=50)


# =========================
# STEP 3 (FACE UPLOAD)
# =========================
class WorkerStep3Form(forms.Form):
    face_image = forms.ImageField(required=False)


# =========================
# STEP 4 (PASSWORD)
# =========================
class WorkerStep4Form(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    # =========================
# STEP 4 (reviews)
# =========================
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 5
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),
        }
        