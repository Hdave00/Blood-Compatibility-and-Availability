from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Donor, BLOOD_TYPES


class UserRegistrationForm(UserCreationForm):
    """ User registration form for letting the user register just a user and not a donor """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class DonorForm(forms.ModelForm):
    """ Donor registration form for letting the user also register as a Donor with extra profile details """
    
    blood_type = forms.ChoiceField(choices=BLOOD_TYPES, required=False)
    location = forms.CharField(max_length=255, required=False, label="Location (Optional)",
            help_text="This is what will be shown to other users of the application, once you accept their request. It can be specific or generalised.")
    city = forms.CharField(max_length=100, required=False, label="City (Required for map)",
            help_text="This is what the app uses to represent availability of donors and subsequent blood types in a given city. This information is private and never exposed.")

    state_or_county = forms.CharField(max_length=100, required=False)

    country = forms.CharField(max_length=100, required=False, label="Country (Required for map)",
            help_text="This is what the app uses to represent availability of donors and subsequent blood types in a given country. This information is private and never exposed.")
    availability = forms.BooleanField(required=False, initial=True, label="Available for blood donation")

    class Meta:
        model = Donor
        fields = ['blood_type', 'location', 'city', 'country', 'state_or_county', 'availability']
