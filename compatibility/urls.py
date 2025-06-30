from django.urls import path
from django.contrib.auth import views as auth_views # not needed yet, might be needed for standardising authentication views later

from . import views


urlpatterns = [

    # non api/simple render endpoint urls here

    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("about/", views.about, name="about"),
    path("donation_history/", views.donation_history, name="donation_history"),

    # fetch the map page and its details, also the the geocode using HERE api key
    path('map/', views.map_view, name='map'),
    path("api/geocode", views.geocode_proxy, name="geocode_proxy"),


    # HERE Map API endpoint urls here

    # path for location of donors
    path("api/donor-locations/", views.donor_locations_api, name="donor_location_api"),


    # Django RESTFUL API endpoint urls here

    # lets user manually enter two blood types and check if they are compatible OR the api compatibility checker for the donor_list.html page
    path("api/check_compatibility/", views.check_compatibility, name="check_compatibility"),
    path("api/check_compatibility/<int:request_id>/", views.check_compatibility, name="check_compatibility"),

    # path for user profile,where the user can see matched donors, requests that match them, make functionality that lets the user click a button and
    # approve or reject the request and sends an email request to both request maker and donor user and sends an in app notification as well.
    path("user/<int:user_id>/profile/", views.profile_page, name="user_profile"),

    # editing user profile
    path("api/edit_profile/", views.edit_profile, name="edit_profile"),

    # this will also be used on the user_profile page to let a reg donor see all their potential matches, calling the match_donors function
    path("api/match_donors/", views.match_donors, name="match_donors"),

    # fetch a list of all donors (for the donor_list page)
    path("donors/", views.donor_list_page, name="donor_list"),
    path("api/donors/", views.donor_list_api, name="donor_list_api"),  # For DRF API (within that page)

    # paths for active requests and its api path
    path("active-requests/", views.active_requests_page, name="active_requests"),
    path("api/active-requests/", views.active_requests_api, name="active_requests_api"), # For DRF API (within that page)

    # fetches details about each donor (for the donor_list page)
    path("api/donor/<int:donor_id>/", views.donor_detail, name="donor_detail"),

    # used in profile page to see and accept incoming requests
    path("accept_request/<int:request_id>/", views.accept_request, name="accept_request"),

    # for sending a request to a donor
    path("api/create_donor_request/<int:recipient_id>", views.create_donor_request, name="create_request"),

    # for managing the request ie, accept and reject request
    path("api/manage_donor_request/<int:request_id>", views.manage_donor_request, name="manage_request"),

    # for loading outgoing requests from a donor to another donor
    path("api/get_outgoing_requests/", views.get_outgoing_requests, name="outgoing_requests"),

    # for cancelling/deleting an outgoing request
    path("cancel_request/<int:request_id>/", views.cancel_request, name="cancel_request"),

    # Fetch active donation requests for a user
    path("api/get_requests/", views.get_requests, name="get_requests"),

]
