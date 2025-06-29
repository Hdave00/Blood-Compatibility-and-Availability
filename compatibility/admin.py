from django.contrib import admin
from .models import User, Donor, DonationRequest, BloodMatchHistory


# UserAdmin
class UserAdmin(admin.ModelAdmin):
    """ User admin model for managing users and their attributes """

    list_display = ('username', 'email', 'location', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'location')
    list_filter = ('is_active', 'location')
    # use fieldsets
    # should be a tuple of fieldset definitions, where each fieldset is a tuple containing a title and a dictionary of options
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'location')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


# DonorAdmin for donor details and manipulation
class DonorAdmin(admin.ModelAdmin):
    """ donor model admin setup for managing donors and their attributes """

    list_display = ('user', 'blood_type', 'location', 'availability', 'date_registered')
    search_fields = ('user__username', 'blood_type', 'location')
    list_filter = ('blood_type', 'availability', 'date_registered')
    readonly_fields = ('date_registered',)

    # should be a tuple of fieldset definitions, where each fieldset is a tuple containing a title and a dictionary of options
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Donation Details', {'fields': ('blood_type', 'location', 'latitude', 'longitude', 'availability')}),
        ('Registration Date', {'fields': ('date_registered',)}),
    )


# ideally want to manage donors within a donation request since, DonationRequest is an instance/model that can be created, multiple times
# TabularInline is a way to display related objects in a tabular format within the parent object’s admin page.
# It’s useful for managing related objects without having to navigate away from the parent object’s page ( description from django docs)
class DonorInline(admin.TabularInline):
    """ manages donors inside a DonationRequest instance """

    model = DonationRequest.donors.through
    extra = 1
    verbose_name = "Potential Donor"
    verbose_name_plural = "Potential Donors"


# DonationRequestAdmin for managing the actual donation request and its attributes
class DonationRequestAdmin(admin.ModelAdmin):
    """ managing donation requests """

    list_display = ('recipient', 'blood_type_needed', 'location', 'status', 'created_at', 'is_accepted')
    search_fields = ('recipient__username', 'blood_type_needed', 'location')
    list_filter = ('status', 'blood_type_needed', 'created_at', 'is_accepted')

    # read only fields are generally ones that are auto-generated and shouldn't be edited, but we still want that related information available.
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Request Information', {'fields': ('recipient', 'blood_type_needed', 'location', 'status')}),
        ('Donor Matching', {'fields': ('donors', 'accepted_donors', 'is_accepted')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )

    # using the inline class we created to see the donation request and inside it as well as in, who is the donor related to the request
    inlines = [DonorInline]
    filter_horizontal = ('donors', 'accepted_donors')

# BloodMatchHistoryAdmin class, to check and track the blood match/compatibility feature AND probably also to track donation history or compatible users
# in the future by storing compatible data.
class BloodMatchHistoryAdmin(admin.ModelAdmin):
    """ tracking blood compatibility checks """

    list_display = ('donor', 'recipient', 'donor_blood', 'recipient_blood', 'is_compatible', 'match_date')
    search_fields = ('donor__user__username', 'recipient__username')
    list_filter = ('is_compatible', 'match_date')
    readonly_fields = ('match_date',)
    
    # should be a tuple of fieldset definitions, where each fieldset is a tuple containing a title and a dictionary of options
    fieldsets = (
        ('Match Details', {'fields': ('donor', 'recipient', 'donation_request')}),
        ('Blood Types', {'fields': ('donor_blood', 'recipient_blood', 'is_compatible')}),
        ('Timestamps', {'fields': ('match_date',)}),
    )


# Register the actual models
admin.site.register(User, UserAdmin)
admin.site.register(Donor, DonorAdmin)
admin.site.register(DonationRequest, DonationRequestAdmin)
admin.site.register(BloodMatchHistory)

