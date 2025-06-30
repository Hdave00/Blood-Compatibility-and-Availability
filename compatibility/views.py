import json
import urllib.parse
import requests

from collections import Counter
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db.models import Q

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User, DonationRequest, BloodMatchHistory, Donor, COMPATIBILITY_CHART, BLOOD_TYPES
from .serializers import DonorSerializer, DonationRequestSerializer, UserSerializer, BloodMatchHistorySerializer
from .utils import is_compatible
from .forms import UserRegistrationForm, DonorForm
from django.conf import settings

# HERE API key at global level
HERE_API_KEY = settings.HERE_API_KEY


def parse_location(location):
    """
    Fetch city, state/county, and country from HERE Maps API.
    Returns city, country, and a formatted location string.
    """
    try:
        response = requests.get(
            "https://geocode.search.hereapi.com/v1/geocode",
            params={"q": location, "apiKey": HERE_API_KEY, "lang": "en"},
        )
        response.raise_for_status()
        result = response.json().get("items", [])

        if result:
            address = result[0]["address"]

            # extract city and country and boroughs for weird american things
            city = address.get("city", address.get("district", ""))
            country = address.get("countryName", "")

            # prioritize state but fallback to county (for UK and other regions)
            state_or_county = address.get("state", address.get("county", ""))

            # formatted location (city, state/county, country)
            formatted_location = ", ".join(filter(None, [city, state_or_county, country]))

            return {
                "city": city,
                "country": country,
                "location": formatted_location,
            }

    except requests.RequestException as e:
        print(f"Error parsing location: {e}")

    return {"city": "", "country": "", "location": "Unknown"}


def login_view(request):
    if request.method == "POST":

        # attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "compatibility/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "compatibility/login.html")


# TODO better donor location HERE Maps API endpoint
def donor_locations_api(request):

    # getting the request params and stripping them
    blood_type = request.GET.get("blood_type", "").strip()
    location = request.GET.get("location", "").strip()

    # using Q object to create complex queries with OR and AND conditions (allows to combine multiple conditions in a query,
    # and to filter results where either one condition or another is true)
    filters = Q(user__is_active=True, availability=True)

    if blood_type:
        filters &= Q(blood_type=blood_type)

    if location:
        filters &= (
            Q(city__icontains=location) |
            Q(state_or_county__icontains=location) |
            Q(country__icontains=location)
        )

    donors = Donor.objects.filter(filters).values(
        'city', 'state_or_county', 'country', 'blood_type'
    )

    # from HERE Maps API we are getting the region data in a dict format so we use a dict here as well
    region_data = {}

    # iterating over donor objects to filter out city, state/county and country from the model feilds
    for donor in donors:
        region_key = ", ".join(filter(None, [donor['city'], donor['state_or_county'], donor['country']]))

        if region_key not in region_data:
            region_data[region_key] = {"count": 0, "blood_counts": Counter()}

        region_data[region_key]["count"] += 1
        region_data[region_key]["blood_counts"][donor["blood_type"]] += 1

    # the response data is being returned as a list, and the lambda keyword is used to create a small anonymous function, which is a value to the key
    # in how we sort the blood types
    response_data = []
    for region, data in region_data.items():
        sorted_blood_types = sorted(data["blood_counts"].items(), key=lambda x: -x[1])
        blood_type_str = ", ".join([f"{bt} {count}" for bt, count in sorted_blood_types])

        response_data.append({
            "region": region,
            "count": data["count"],
            "blood_types": blood_type_str
        })

    return JsonResponse(response_data, safe=False)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# updated register view with HERE api reference
def register(request):
    """ registers a user as a normal User OR as a Donor:
     Uses HERE Maps Autocomplete API to get consistent and accurate location data.
      Also uses Geolocation API to to get precise coordinate based location.
       Registration is handled by custom built Django forms. """

    if request.method == "POST":
        print("recieved post request", request.POST)

        user_form = UserRegistrationForm(request.POST)
        donor_form = DonorForm(request.POST)

        # check user validity
        if user_form.is_valid():
            print("user_form is valid:", user_form.cleaned_data)
            user = user_form.save()

            # save donor details only if blood_type is provided
            if donor_form.is_valid() and donor_form.cleaned_data.get('blood_type'):
                print("donor_form is valid", donor_form.cleaned_data)
                donor = donor_form.save(commit=False)
                donor.user = user

                # capture city, country, and state_or_county
                donor.city = donor_form.cleaned_data.get('city', "")
                donor.country = donor_form.cleaned_data.get('country', "")
                state_or_county = donor_form.cleaned_data.get('state_or_county', "")

                # update location in 'City, State/County, Country' format
                donor.update_location(state_or_county)
                donor.save()

            login(request, user)
            return redirect("index")

        # show errors from django forms if errors arise (graceful handling)
        else:
            print("user_form errors:", user_form.errors)
            print("donor_form errors:", donor_form.errors)

    # show the form again with already filled in fields still filled in and errors underlines
    else:
        print("GET request received")
        user_form = UserRegistrationForm()
        donor_form = DonorForm()

    return render(request, "compatibility/register.html", {
        "user_form": user_form,
        "donor_form": donor_form,
        "HERE_API_KEY": settings.HERE_API_KEY,
    })



# Edit profile function to be able to edit their info and delete profile if needed
@login_required
def edit_profile(request):
    """ View that allows the user to edit or delete their profile """

    user = request.user

    # safely get the donor profile if it exists
    donor_profile = getattr(user, "donor_profile", None)

    # pass json data if GET request for the edit profile page
    if request.method == "GET":
        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "blood_type": donor_profile.blood_type if donor_profile else None,
            "location": donor_profile.location if donor_profile else None,
            "city": donor_profile.city if donor_profile else None,
            "state_or_county": donor_profile.state_or_county if donor_profile else None,
            "country": donor_profile.country if donor_profile else None,
            "blood_types": BLOOD_TYPES,
        })

    # if post, check if the changed data is valid, then return new response
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        new_username = data.get("username", "").strip()
        new_blood_type = data.get("blood_type", "").strip()
        new_location = data.get("location", "").strip()

        # handle edge case of missing username
        if not new_username:
            return JsonResponse({"error": "Username cannot be empty."}, status=400)

        # update user fields
        user.username = new_username
        user.save()

        # handle new location
        if new_location:
            location_data = parse_location(new_location)

            print("Before update - Location:", donor_profile.location)
            print("Before update - City:", donor_profile.city)
            print("Before update - Country:", donor_profile.country)

            # assign new values
            donor_profile.city = location_data["city"]
            donor_profile.country = location_data["country"]
            state_or_county = location_data.get("state_or_county", None)

            # save the correctly formatted location
            donor_profile.location = location_data["location"]

            # explicitly assign state/county
            if state_or_county:
                donor_profile.state_or_county = state_or_county

            print("After assignment - Location:", donor_profile.location)
            print("After assignment - City:", donor_profile.city)
            print("After assignment - Country:", donor_profile.country)

            # save changes
            donor_profile.save()

            print("After save - Location:", donor_profile.location)

        # new data response
        return JsonResponse({
            "message": "Profile updated successfully",
            "username": user.username,
            "blood_type": donor_profile.blood_type if donor_profile else None,
            "location": donor_profile.location,
            "city": donor_profile.city,
            "state_or_county": donor_profile.state_or_county,
            "country": str(donor_profile.country),  # ensure country is a string
        })

    # letting the user delete the profile
    elif request.method == "DELETE":
        user.delete()
        return JsonResponse({"message": "Account deleted successfully"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# Function for fetching donors for HERE map API (on the donor_list page)
@api_view(["GET"])
def donor_list_api(request):
    """ Returns JSON response with all available donors (filtered by blood type & country) """

    # getting the data for the blood type and if the blood_type string contains spaces, they will be replaced with + this ie because spaces
    # tend to break the accuracy of the blood type
    blood_type = request.GET.get("blood_type", "").replace(" ", "+")
    # removes any leading and trailing whitespace from the country string. If the country string is empty or only contains spaces,
    # strip will return an empty string
    country = request.GET.get("country", "").strip()

    # select only donors that have checked the availability box ie, agreed to be a donor
    donors = Donor.objects.filter(availability=True).select_related("user")

    if blood_type:
        donors = donors.filter(blood_type=blood_type)
    if country:
        donors = donors.filter(country__iexact=country)

    donor_serializer = DonorSerializer(donors, many=True)

    return Response({"donors": donor_serializer.data})



@api_view(["GET"])
def active_requests_api(request):
    """ Returns JSON response with active donation requests, filtered by blood type and country if provided """

    # get the filter values from request parameters by stripping any whitespace
    blood_type = request.GET.get("blood_type", "").strip()
    country = request.GET.get("country", "").strip()

    # base queryset (only pending or matched requests)
    active_requests = DonationRequest.objects.filter(status__in=["Pending", "Matched"]).select_related("requester")

    # apply filters if provided, only using strip method on country as it is freely typed and not selected from a set value
    if blood_type:
        active_requests = active_requests.filter(blood_type_needed=blood_type)
    if country:
        active_requests = active_requests.filter(country__iexact=country.strip())

    # serialize results
    request_serializer = DonationRequestSerializer(active_requests, many=True)

    return Response({"active_requests": request_serializer.data})



# handles html page stuff for active requests page
@login_required
def active_requests_page(request):
    """ Renders the active requests page with filtering options """

    # fetch active donation requests
    active_requests = DonationRequest.objects.filter(status__in=["Pending", "Matched"]).select_related("requester")

    # ensure blood_types (list of tuples in models.py) is available in the template
    blood_types = BLOOD_TYPES

    # pagination (from django pagination docs, 15 requests per page)
    paginator = Paginator(active_requests, 15)
    page_number = request.GET.get("page")
    active_requests = paginator.get_page(page_number)

    return render(request, "compatibility/active_requests.html", {
        "active_requests": active_requests,
        "blood_types": blood_types,
        "selected_country": request.GET.get("country", "").strip(),
    })


# function fetches the details of a single donor, so that id can be displayed where needed and changes can be made easier
@api_view(["GET"])
def donor_detail(request, donor_id):
    """ returns details of a single donor """

    try:
        donor = Donor.objects.get(id=donor_id)
        serializer = DonorSerializer(donor)
        return Response(serializer.data)
    except Donor.DoesNotExist:
        return Response({"error": "Donor not found"}, status=404)

@login_required
def donor_list_page(request):
    """ Renders the donor list page with filtering options """

    # using the same strip methods on filters for the donor list page(donor_list.html)
    blood_type_filter = request.GET.get("blood_type", "").strip()
    country_filter = request.GET.get("country", "").strip()

    donors = Donor.objects.filter(availability=True)

    # apply filter if selected
    if blood_type_filter:
        donors = donors.filter(blood_type=blood_type_filter)
    if country_filter:
        donors = donors.filter(country__iexact=country_filter)

    return render(request, "compatibility/donor_list.html", {
        "donors": donors,
        "blood_types": BLOOD_TYPES,
        "selected_blood_type": blood_type_filter,
        "selected_country": country_filter,
    })



# renders donation history page
def donation_history(request):
    """ renders the donation history page which shows the history of requests """

    # get filters from the query parameters
    blood_type_filter = request.GET.get('blood_type')
    status_filter = request.GET.get('status')
    city_filter = request.GET.get('city')
    country_filter = request.GET.get('country')

    # base queryset (all donation requests) (similar to donor_list)
    donation_requests = DonationRequest.objects.all().order_by('-created_at')

    # apply filters if provided
    if blood_type_filter:
        donation_requests = donation_requests.filter(blood_type_needed=blood_type_filter)
    if status_filter:
        donation_requests = donation_requests.filter(status=status_filter)
    if city_filter:
        donation_requests = donation_requests.filter(city__icontains=city_filter)
    if country_filter:
        donation_requests = donation_requests.filter(country__icontains=country_filter)


    # pagination (10 requests per page)
    paginator = Paginator(donation_requests, 10)
    page_number = request.GET.get('page')
    donation_requests = paginator.get_page(page_number)

    # retrieve STATUS_CHOICES from the DonationRequest model
    status_choices = DonationRequest.STATUS_CHOICES

    # pass variables/context to the template
    return render(request, 'compatibility/donation_history.html', {
        'donation_requests': donation_requests,
        'blood_types': BLOOD_TYPES,
        'status_choices': status_choices,
        'selected_blood_type': blood_type_filter,
        'selected_status': status_filter,
        'selected_city': city_filter,
        'selected_country': country_filter,
    })



@login_required
def create_donor_request(request, recipient_id):
    """ allows a donor to create a request for a blood donation from another donor """

    if request.method == "POST":

        # check if logged in user is a registered donor
        current_user = request.user
        if not hasattr(current_user, "donor_profile"):
            return JsonResponse({"error": "Only registered donors can make donation requests"}, status=403)

        # get the donor being requested
        recipient = get_object_or_404(User, id=recipient_id)

        # ensure recipient is also a donor
        recipient_donor_profile = getattr(recipient, "donor_profile", None)
        if not recipient_donor_profile:
            return JsonResponse({"error": "Recipient is not a registered donor"}, status=400)

        # ensure donor isnt requestting themselves
        if current_user == recipient:
            return JsonResponse({"error": "Cannot request a donation from yourself"}, status=400)

        # check if a request already exists
        existing_request = DonationRequest.objects.filter(
            recipient=recipient,
            donors=request.user.donor_profile,
            status='Pending').exists()

        if existing_request:
            return JsonResponse({"error": "You have already requested from this donor"}, status=400)

        # create the request for donation, select the relevant fields form the DonationRequest model
        donation_request = DonationRequest.objects.create(
            recipient=recipient,
            blood_type_needed=current_user.donor_profile.blood_type,
            location=current_user.donor_profile.location,
            status='Pending',
            requester=request.user
        )
        donation_request.donors.add(current_user.donor_profile)

        return JsonResponse({"message": "Request Sent."})

    return JsonResponse({"error": "Invalid request method."}, status=405)



@login_required
def manage_donor_request(request, request_id):
    """ allows a donor who has requests from other donors, to accept or decline a donation request """

    if request.method == "POST":

        # handle the case that the request is being edited/managed by the current logged in user
        donation_request = get_object_or_404(DonationRequest, id=request_id)
        if donation_request.recipient != request.user:
            return JsonResponse({"error": "You can only manage requests made to you, not others."}, status=403)

        # dynamically updating the request state for instant changes, not needing a refresh of the page
        data = json.loads(request.body)
        action = data.get("action")

        # accept request
        if action == "accept":
            for donor in donation_request.donors.all():
                donation_request.accept_request(donor)

            return JsonResponse({"message": "Request accepted."})

        # reject request
        if action == "reject":
            donation_request.delete()
            return JsonResponse({"message": "Request rejected."})

        return JsonResponse({"error": "Invalid action."}, status=400)

    return JsonResponse({"error": "invalid request method"}, status=405)


# This function only renders index.html. All the login-based logic will be handled in the login template.
# Displays information about the web app and options for blood matching and donations
def index(request):
    """ homepage function where the user can see what the web-app is about and passing the statistic data """

    # get the donor count
    total_donors = Donor.objects.count()

    # Fetch the latest donation requests (limit to last 5) by date of creation, and limit query to 6 using slicing
    recent_donations = DonationRequest.objects.order_by("-created_at")[:6]

    # from the donor model use the country, city and state field to get the count of users registered therein to display on index.html
    # use distinct() in django to get the required field data then we cna count all we need
    total_countries = Donor.objects.values("country").distinct().count()
    total_cities = Donor.objects.values("city").distinct().count()
    total_states_or_counties = Donor.objects.values("state_or_county").distinct().count()
    total_blood_types = Donor.objects.values("blood_type").distinct().count()

    return render(request, "compatibility/index.html", {
        "total_donors": total_donors,
        "recent_donations": recent_donations,
        "total_countries": total_countries,
        "total_cities": total_cities,
        "total_states_or_counties": total_states_or_counties,
        "total_blood_types": total_blood_types,
    })



def about(request):
    """ renders the about page template """

    return render(request, "compatibility/about.html")


# Finds compatible donors for a recipient based on blood type and location, the system will fetch eligible donors using a compatibility algorithm
# is designed to find compatible donors for a recipient, and it returns the data as JSON.
# This is used for the match donors api endpoint on the user_profile.html template
@login_required
def match_donors(request):
    """ Find and return both accepted and potential matches for the logged-in user """

    user = request.user

    # ensure the user is a donor
    if not hasattr(user, 'donor_profile'):
        return JsonResponse({"error": "You must be a registered donor to find matches."}, status=400)

    # get the current users blood type
    user_blood_type = user.donor_profile.blood_type

    # get all donation requests where the user is the recipient
    donation_requests = DonationRequest.objects.filter(recipient=user)

    # collect accepted matches from existing donation requests
    matches = [
        {
            "username": donor.user.username,
            "blood_type": donor.blood_type,
            "email": donor.user.email,
            "location": donor.location if donor.location and donation_request.is_accepted else "Hidden until accepted",
            "is_accepted": True,
            "id": donor.user.id,
        }
        for donation_request in donation_requests
        for donor in donation_request.accepted_donors.all()
    ]

    # gather IDs of all donors already involved in requests (accepted or pending)
    requested_donor_ids = {
        donor.id
        for donation_request in donation_requests
        for donor in donation_request.donors.all()
    }

    # find new potential donors who are compatible but not in the request history
    potential_donors = Donor.objects.exclude(user=user)
    compatible_potential_donors = [
        donor for donor in potential_donors if is_compatible(donor.blood_type, user_blood_type)
    ]

    # add potential matches to the list by extending the matches list (always hide location until accepted)
    matches.extend([
        {
            "username": donor.user.username,
            "blood_type": donor.blood_type,
            "email": donor.user.email,
            "location": "Hidden until accepted",
            "is_accepted": False,
            "id": donor.user.id,  # use user.id instead of donor.id to avoid referencing wrong IDs as Users and Donors have separate IDs
        }
        for donor in compatible_potential_donors
    ])

    return JsonResponse({"matches": matches}, status=200)



@login_required
def accept_request(request, request_id):
    """ lets a donor accept an incoming request """

    if request.method == "POST":
        donation_request = get_object_or_404(DonationRequest, id=request_id)

        # ensure user is a registered donor (reference related name in "user" feild)
        try:
            donor = request.user.donor_profile
        except Donor.DoesNotExist:
            return JsonResponse({"error": "Please register as a donor to accept this request"}, status=403)

        # check if donor is eligible to accept ie, checking via the COMPATIBILITY_CHART in models, to verify compatibility bw request and donor
        if donor not in donation_request.find_potential_donors():
            return JsonResponse({
                "error": "You are not eligible to accept this request as the blood types are not mutually compatible. "}, status=403)

        # accept the request and update the status
        donation_request.accept_request(donor)

        return JsonResponse({
            "message": "request accepted",
            "donor_email": donor.user.email,
            "donor_location": donor.location
        })
    return JsonResponse({"error": "invalid request"}, status=400)


# function to get a request for the user that the request was sent to, on their profile when the user visits user_profile.html
@login_required
def get_requests(request):
    """ Fetch and display active donation requests """

    # ensure user is a donor
    current_user = request.user
    if not hasattr(current_user, "donor_profile"):
        return JsonResponse({"error": "You must be a registered donor to view requests."}, status=400)

    # fetch pending requests where the current logged-in user is the recipient
    pending_requests = DonationRequest.objects.filter(
        recipient=current_user,
        status="Pending",
    ).select_related("requester", "recipient")

    # prepare JSON response
    requests_data = [{
        "id": req.id,
        "requester_username": req.requester.username,
        "blood_type_needed": req.blood_type_needed,
        "created_at": req.created_at.strftime("%Y-%m-%d %H:%M"),
        "recipient": req.recipient.id,
    } for req in pending_requests]

    return JsonResponse({"requests": requests_data})


@login_required
def get_outgoing_requests(request):
    """ API endpoint view that fetches outgoing requests for the logged in user """

    # get the request object from the donor where the status is pending
    outgoing_requests = DonationRequest.objects.filter(donors=request.user.donor_profile, status="Pending")
    data = [
        {
            "id": req.id,
            "recipient_username": req.recipient.username,
            "blood_type_needed": req.blood_type_needed,
        }
        for req in outgoing_requests
    ]
    return JsonResponse({"requests": data})


@login_required
@csrf_exempt
def cancel_request(request, request_id):
    """ view handles the cancelling/deleting of a request sent by the user """

    if request.method == "DELETE":
        try:
            donation_request = DonationRequest.objects.get(id=request_id, requester=request.user)

            # ensure only "Pending" requests can be cancelled
            if donation_request.status == "Pending":
                donation_request.delete()
                return JsonResponse({"success": True, "message": "Request cancelled."})
            else:
                return JsonResponse({"success": False, "error": "Request cannot be cancelled."})

        except DonationRequest.DoesNotExist:
            return JsonResponse({"success": False, "error": "Request not found."})

    return JsonResponse({"success": False, "error": "Invalid request method."})



# Displays user details, including blood type, donation history, and compatibility.
# allow users to view their past blood donations and requests(probably just a static view for a user, in the user page)
# IMP:- using the get_user_model for only the register and user_profile functions for scalability of different user types later on
@login_required
def profile_page(request, user_id):
    """ view that renders the user's profile page and allows the functionality for
     1- deleting their profile,
     2- editing their profile details and saving them asynchonously,
     3- seeing auto-matched donors,
     4- cancelling requests and accepting/rejecting incoming requests """

    # fetch the profile being viewed
    viewed_user = get_object_or_404(User.objects.select_related('donor_profile'), id=user_id)

    # check if the current user is viewing their own profile
    current_user = request.user
    is_own_profile = current_user == viewed_user

    # get donor profiles (if they exist, use None if not)
    donor_profile = getattr(viewed_user, 'donor_profile', None)
    current_donor_profile = getattr(current_user, 'donor_profile', None)

    # fetch all donation requests for the viewed user (as a recipient)
    received_requests = DonationRequest.objects.filter(
        recipient=viewed_user
    ).select_related('recipient').prefetch_related('donors', 'accepted_donors')

    # check if the logged-in donor has already made a request (for 'Request' button visibility)
    has_requested = False
    if current_donor_profile and donor_profile:
        has_requested = received_requests.filter(
            donors=current_donor_profile, status='Pending'
        ).exists()

    # fetch donor contact info if a request is accepted (for displaying sensitive info)
    donor_contact_info = {"email": "Hidden until accepted", "location": "Hidden until accepted"}
    if current_donor_profile and donor_profile:
        accepted_request = received_requests.filter(
            donors=current_donor_profile, is_accepted=True
        ).first()
        if accepted_request:
            donor_contact_info = accepted_request.donor_contact_info(current_donor_profile)

    # fetch pending outgoing requests (only if viewing your own profile)
    pending_requests = DonationRequest.objects.filter(
        requester=current_user, status='Pending'
    ).select_related('recipient', 'requester') if is_own_profile else None

    # log and pass context
    print(donor_profile.location)
    return render(request, "compatibility/user_profile.html", {
        "viewed_user": viewed_user,
        "donor_profile": donor_profile,
        "received_requests": received_requests,
        "is_own_profile": is_own_profile,
        "has_requested": has_requested,
        "donor_contact_info": donor_contact_info,
        "blood_types": BLOOD_TYPES,
        "pending_requests": pending_requests,
        "date_registered": donor_profile.date_registered if donor_profile else None,
    })



# view for A form where users input donor/recipient blood types to check compatibility MANUALLY
# Users can input donor and recipient blood types into a form (HTML EMBED) OR also pass in ajax requests to the server for instant compatibility check
def check_compatibility(request, request_id=None):
    """ Publicly accessible Blood Compatibility Checker
     Or if request_id is provided:
        - Check if the logged-in donor is compatible with the donation request. """

    # get valid blood types from the global list of tuples in models
    blood_types = [bt[0] for bt in BLOOD_TYPES]

    # donor compatibility check when request_id is provided
    if request_id:
        donation_request = get_object_or_404(DonationRequest, id=request_id)

        # ensure the user is a donor
        if not hasattr(request.user, "donor_profile"):
            return JsonResponse({"error": "Only registered donors can check compatibility."}, status=403)

        # get donor and recipient blood
        donor_blood = request.user.donor_profile.blood_type
        recipient_blood = donation_request.blood_type_needed

        # run the is_compatible function from utils.py, on donor and recipient blood to prompt a message in script.js about whether the donor
        # and recipient are compatible
        compatible = is_compatible(donor_blood, recipient_blood)

        return JsonResponse({
            "donor_blood": donor_blood,
            "recipient_blood": recipient_blood,
            "is_compatible": compatible
        })

    # handle manual blood type check for public use, this is in the check_compatibility.html template where the user inputs two blood types
    # and checks if they are compatible
    donor_blood = request.GET.get("donor_blood", "").strip().upper()
    recipient_blood = request.GET.get("recipient_blood", "").strip().upper()

    # checking if the request is an AJAX request, handle AJAX requests for manual checks
    # Note:- AJAX requests often include the X-Requested-With header set to XMLHttpRequest
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if not donor_blood or not recipient_blood:
            return JsonResponse({"error": "Both blood types must be selected"}, status=400)

        # handle invalid selection of blood types
        if donor_blood not in blood_types or recipient_blood not in blood_types:
            return JsonResponse({"error": "Invalid blood type selection"}, status=400)

        # run the same is_compatible function as before but this time on the page itself, with manually provided blood types
        compatible = is_compatible(donor_blood, recipient_blood)

        return JsonResponse({
            "donor_blood": donor_blood,
            "recipient_blood": recipient_blood,
            "is_compatible": compatible
        })

    # render page for manual blood type checking, convert the python object into a JSON string, using json.dumps. For sending data over the web
    # then in script.js, use JSON.parse() to convert it back into a JS object, so we can work with same data in JS as well.
    return render(request, "compatibility/check_compatibility.html", {
        "blood_types": blood_types,
        "compatibility_chart": json.dumps(COMPATIBILITY_CHART)
    })


def geocode_proxy(request):
    """ api interactins in the backend only """

    query = request.GET.get("q")
    if not query:
        return JsonResponse({"error": "Missing query"}, status=400)

    response = requests.get(
        "https://geocode.search.hereapi.com/v1/geocode",
        params={"q": query, "apiKey": HERE_API_KEY}
    )

    return JsonResponse(response.json())


# Map-based Donor Search, using Here Maps API
def map_view(request):
    """ Displays available donors on a map using a Maps API """

    return render(request, "compatibility/map.html", {
        "here_api_key": HERE_API_KEY
    })


# not possible yet- a notification system that alerts users when a match is found or when their request status changes
@login_required
def notifications(request):
    """ view that notifies users when a match is found for their request """


