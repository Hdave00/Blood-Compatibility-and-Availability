// Helper: gets a CSRF token (improves security, in theory atleast, if i havent forgotten to actually use it in API calls)
function getCSRFToken() {
    // first, try the <meta> tag approach (modern/preferred for fetch requests according to django docs)
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) return metaToken.getAttribute("content");

    // backup, look for hidden input field (for traditional forms)
    const inputToken = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (inputToken) return inputToken.value;

    // if not found, alert the user and log the error
    console.error("CSRF token not found. Ensure {% csrf_token %} or <meta> is present.");
    showAlert("Error: CSRF token is missing. Please refresh the page.");
    return null;
}

// call each main function only on the page it exists as seen in project3
document.addEventListener("DOMContentLoaded", () => {

    // debugging potential csrf issues and making sure the respective page is loaded and its functions called
    console.log("Page loaded, script initialized.");
    console.log("CSRF Token:", getCSRFToken());


        // only initialize features on the correct pages
        if (document.getElementById("profile-container")) {
            setupProfilePage();
        }

        if (document.getElementById("pendingRequestsList")) {
            loadPendingRequests();
        }

        // Cancel section
        if (document.getElementById("outgoingRequestsList")) {
            loadOutgoingRequests();
        }

        if (document.getElementById("compatibility-data")) {
            setupCheckCompatibility();
        }

        const locationInput = document.getElementById("locationAutocomplete");
        if (locationInput) {
            console.log("Location Autocomplete is being initialized...");
            const cityInput = document.getElementById("id_city");
            const countryInput = document.getElementById("id_country");
            const latitudeInput = document.getElementById("id_latitude");
            const longitudeInput = document.getElementById("id_longitude");

            initLocationAutocomplete(locationInput, cityInput, countryInput, latitudeInput, longitudeInput);
        }

        if (document.getElementById("matchedDonorsSection")) {
            setupMatchDonors();
        }
        console.log("match donors called", setupMatchDonors); // debug

        if (document.getElementById("donorList")) {
            setupDonorList();
        }

        if (document.getElementById("requestList")) {
            setupActiveRequests();
        }

        if (document.getElementById("toggleMatches")) {
            setupToggleMatches();
        }

        const checkLocalBtn = document.getElementById("checkBloodLocalBtn");
        const checkAPIBtn = document.getElementById("checkBloodAPIBtn");

        if (checkLocalBtn) checkLocalBtn.addEventListener("click", checkBloodCompatibilityLocal);
        if (checkAPIBtn) checkAPIBtn.addEventListener("click", checkBloodCompatibilityAPI);

});


// Function: Profile Page Handlers
function setupProfilePage() {
    const profileContainer = document.getElementById("profile-container");
    if (!profileContainer) return;

    // buttons
    const editBtn = document.getElementById("editProfile");
    const saveBtn = document.getElementById("saveChanges");
    const cancelBtn = document.getElementById("cancelEdit");
    const deleteBtn = document.getElementById("deleteAccount");
    const form = document.getElementById("edit-profile-form");
    if (!form) return;

    // user details
    const displayUsername = document.getElementById("display-username");
    const displayEmail = document.getElementById("display-email");
    const displayBloodType = document.getElementById("display-blood-type");
    const displayLocation = document.getElementById("display-location");
    const displayMemberSince = document.getElementById("display-member-since");

    // input fields
    const inputUsername = document.getElementById("username");
    const inputBloodType = document.getElementById("blood_type");
    const inputLocation = document.getElementById("locationAutocomplete");

    // create hidden inputs for city, country, state_or_county, latitude, and longitude
    const cityInput = createHiddenInput("id_city");
    const countryInput = createHiddenInput("id_country");
    const stateOrCountyInput = createHiddenInput("id_state_or_county");
    const latInput = document.getElementById("id_latitude");   // match existing HTML
    const lngInput = document.getElementById("id_longitude");

    form.append(cityInput, countryInput, stateOrCountyInput, latInput, lngInput);

    // helper function to create a hidden input mainly to capture location details separately
    function createHiddenInput(id) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.id = id;
        return input;
    }

    // ensure location autocomplete updates hidden fields, because location capture is happeneing with a single "location" input feild that then,
    // separates into city/borough, state/county and country, by using HERE Autocomplete API.
    if (inputLocation) {
        initLocationAutocomplete(inputLocation, cityInput, countryInput, stateOrCountyInput, latInput, lngInput);
    }

    // get the email and display it 
    if (displayEmail && !document.getElementById("email")) {
        const emailField = document.createElement("div");
        emailField.className = "mb-3";
        emailField.innerHTML = `
            <label class="form-label"><strong>Email (Non-editable)</strong></label>
            <input type="email" id="email" class="form-control" value="${displayEmail.textContent.trim()}" disabled>
        `;
        form.insertBefore(emailField, form.children[1]);
    }

    // display member since, ie, created at field
    if (displayMemberSince && displayMemberSince.textContent.trim()) {
        const rawDate = new Date(displayMemberSince.textContent.trim());
        displayMemberSince.textContent = rawDate.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    }

    form.classList.add("d-none");

    // function to toggle the edit mode in a person's profile page, create the buttons, 
    function toggleEditMode(showEdit) {
        form.classList.toggle("d-none", !showEdit);
        saveBtn.classList.toggle("d-none", !showEdit);
        cancelBtn.classList.toggle("d-none", !showEdit);
        editBtn.classList.toggle("d-none", showEdit);
    }

    // then set the conditions for edit and cancel buttons 
    editBtn?.addEventListener("click", () => toggleEditMode(true));
    cancelBtn?.addEventListener("click", () => toggleEditMode(false));

    // then show the save button only if there are changes detected
    saveBtn?.addEventListener("click", () => {
        if (!inputUsername || !inputBloodType || !inputLocation) {
            console.error("Form elements missing.");
            return;
        }

        // capture all updated data, including state_or_county
        const updatedData = {
            username: inputUsername.value.trim(),
            blood_type: inputBloodType.value,
            location: inputLocation.value.trim(),
            city: cityInput.value.trim(),
            state_or_county: stateOrCountyInput.value.trim(),
            country: countryInput.value.trim(),
            latitude: parseFloat(latInput.value) || null,
            longitude: parseFloat(lngInput.value) || null,
        };

        // debug
        console.log("Final Data to be Sent:", updatedData);

        fetch(`/api/edit_profile/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(updatedData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showNotification("Error: " + data.error);
                } else {
                    showNotification("Profile updated successfully!");

                    displayUsername.textContent = updatedData.username || "N/A";
                    displayBloodType.textContent = updatedData.blood_type || "Not provided";

                    console.log("Final Display Values:", updatedData.city, updatedData.state_or_county, updatedData.country);

                    // update location display in "City, State/County, Country" format
                    displayLocation.textContent = [
                        updatedData.city,
                        updatedData.state_or_county,
                        updatedData.country,
                    ].filter(Boolean).join(", ") || "Not provided";

                    toggleEditMode(false);
                }
            })
            .catch(error => console.error("Error updating profile:", error));
    });

    // if delete button pressed
    deleteBtn?.addEventListener("click", () => {
        if (confirm("Are you sure you want to delete your account?")) {
            fetch(`/api/edit_profile/`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            })
                .then(response => response.json())
                .then(data => {
                    showAlert(data.message);   // show the message and send user back to index/home page
                    window.location.href = "/";
                })
                .catch(error => console.error("Error deleting account:", error));  // catch and log error
        }
    });
}


// HERE Maps API & Geolocation Integration
function initLocationAutocomplete(locationInput, cityInput, countryInput, stateOrCountyInput, latitudeInput, longitudeInput) {
    console.log("initializing HERE location autocomplete");

    const apiKey = "REMOVED";
    const service = new H.service.Platform({ apikey: apiKey }).getSearchService();
    const detectButton = document.getElementById("autodetectLocation");

    let debounceTimer;

    // autocomplete for manual selection
    locationInput.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        if (this.value.length > 2) {
            debounceTimer = setTimeout(() => {
                service.autosuggest(
                    {
                        q: this.value,
                        at: "20.5937,78.9629",
                        limit: 5,
                        lang: "en" // english results
                    },
                    (result) => showSuggestions(result.items),
                    console.error
                );
            }, 300);
        }
    });

    // Auto-detect location using Geolocation API
    detectButton.addEventListener("click", function () {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;

                    service.reverseGeocode(
                        { at: `${latitude},${longitude}`, lang: "en" },  // add "lang: en" parameter to only display names of places in english
                        (result) => {
                            const location = result.items[0]?.address;
                            if (location) {
                                locationInput.value = `${location.city || ''}, ${location.county || location.state || ''}, ${location.countryName || ''}`;
                                cityInput.value = location.city || "";
                                stateOrCountyInput.value = location.county || location.state || "";
                                countryInput.value = location.countryName || "";
                                latitudeInput.value = latitude;
                                longitudeInput.value = longitude;
                            } else {
                                alert("Location not found. Try again.");
                            }
                        },
                        (error) => alert("Reverse geocoding failed: " + error.message)
                    );
                },
                (error) => alert("Geolocation failed: " + error.message)
            );
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    });

    // display autocomplete suggestions
    function showSuggestions(suggestions) {
        // remove any existing suggestion box before creating a new one, using the .remove() method
        let existingBox = document.querySelector(".suggestions-container");
        if (existingBox) existingBox.remove();

        if (!suggestions.length) return;  // if no suggestions for the unputted text, stop function and return

        // create suggestions box
        const suggestionBox = document.createElement("div");
        suggestionBox.className = "suggestions-container";

        suggestions.forEach((suggestion) => {
            const item = document.createElement("div");
            item.className = "suggestion-item";
            item.textContent = suggestion.title;

            item.addEventListener("click", () => {
                console.log("Selected suggestion:", suggestion);

                // extract city, state, and country from title
                const titleParts = suggestion.title.split(", ").map(part => part.trim());
                let extractedCity = titleParts[0] || "";
                let extractedStateOrCounty = titleParts.length > 2 ? titleParts[1] : "";
                let extractedCountry = titleParts.length > 1 ? titleParts[titleParts.length - 1] : "";

                // update input fields, since the api has issues and returns ", ," in the suggestion box, regular expressions are used here
                // regular expression /, ,/g is looking for occurrences of , , in the string.
                // The g at the end stands for "global," will replace all occurrences, not just the first one.
                // The second parameter, "", is what the matched occurrences will be replaced with ie, in this case, an empty string, effectively removing them.
                locationInput.value = `${extractedCity}, ${extractedStateOrCounty}, ${extractedCountry}`.replace(/, ,/g, "").trim();
                cityInput.value = extractedCity;
                stateOrCountyInput.value = extractedStateOrCounty;
                countryInput.value = extractedCountry;

                if (latitudeInput && suggestion.position?.lat) {
                    latitudeInput.value = suggestion.position.lat;
                }
                if (longitudeInput && suggestion.position?.lng) {
                    longitudeInput.value = suggestion.position.lng;
                }

                console.log("Formatted Location:", locationInput.value);
                console.log("Latitude:", latitudeInput.value);

                suggestionBox.remove(); // remove the suggestion box after selection
            });

            suggestionBox.appendChild(item);
        });

        // appending the suggestionbox to the correct div id to make sure it appears where we want it to
        document.body.appendChild(suggestionBox);
        positionSuggestionBox(suggestionBox);

        // close suggestions when clicking outside the input field
        document.addEventListener("click", (e) => {
            if (!locationInput.contains(e.target) && !suggestionBox.contains(e.target)) {
                suggestionBox.remove();
            }
        }, { once: true });
    }

    // position suggestion box under input
    function positionSuggestionBox(suggestionBox) {
        const rect = locationInput.getBoundingClientRect();
        suggestionBox.style.position = "absolute";
        suggestionBox.style.top = `${rect.bottom + window.scrollY}px`;
        suggestionBox.style.left = `${rect.left + window.scrollX}px`;
        suggestionBox.style.width = `${rect.width}px`;
        suggestionBox.style.zIndex = "1000";
    }

    // validate location on form submission
    function validateLocation() {
        if (!cityInput.value || !countryInput.value) {
            alert("Please provide a valid city and country.");
            return false;
        }
        return true;
    }

    // validate the location ie, make sure its correct and exists in HERE autocomplete's dbase before submitting
    document.querySelector("form").addEventListener("submit", validateLocation);

    // inject styles for suggestions, for the suggestion box and the items therein
    const style = document.createElement("style");
    style.innerHTML = `
        .suggestions-container {
            border: 1px solid #ccc;
            border-radius: 5px;
            background: white;
            position: absolute;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
        }
        .suggestion-item {
            padding: 10px;
            cursor: pointer;
        }
        .suggestion-item:hover {
            background: #f8d7da;
        }
    `;
    document.head.appendChild(style);
}



// fetch and display outgoing requests for the current user when in the own profile ie, user_profile.html (with cancel button)
function loadOutgoingRequests() {
    fetch(`/api/get_outgoing_requests/`)
        .then(response => response.json())
        .then(data => {
            const outgoingList = document.getElementById("outgoingRequestsList");
            if (!outgoingList) return;

            // clear current content
            outgoingList.innerHTML = "";

            // if there are no requests after looking at the request data, display/change the innerHTML to say so.
            if (!data.requests || data.requests.length === 0) {
                outgoingList.innerHTML = `<li class="list-group-item text-muted">No outgoing requests.</li>`;
                return;
            }

            // else show the requests with a cancel button that cancel the request
            data.requests.forEach(request => {
                const item = document.createElement("li");
                item.id = `request-${request.id}`;
                item.className = "list-group-item d-flex justify-content-between align-items-center";
                item.innerHTML = `
                    <span>
                        Request to: <strong>${request.recipient_username}</strong>
                        (Blood Type: ${request.blood_type_needed})
                    </span>
                    <button class="btn btn-danger btn-sm cancel-request" data-request-id="${request.id}">
                        Cancel
                    </button>
                `;

                outgoingList.appendChild(item);
            });

            // attach event listeners for cancel requests
            setupCancelRequest();
        })
        .catch(error => console.error("Error fetching outgoing requests:", error));
}

// attach cancel event listeners to outgoing requests, giving the cancel button in the loadOutgoingRequests() function the ability to delete the request
function setupCancelRequest() {
    document.querySelectorAll(".cancel-request").forEach((button) => {
        button.addEventListener("click", (e) => {
            const requestId = e.target.dataset.requestId;
            if (confirm("Are you sure you want to cancel this request?")) {
                cancelRequest(requestId);
            }
        });
    });
}

// Handle cancel request, creating the functionality using the DELETE method to actually cancel the request by deleting it.
function cancelRequest(requestId) {
    fetch(`/cancel_request/${requestId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": getCSRFToken(),
        },
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then((data) => {
        if (data.success) {
            // remove cancelled request from the UI
            document.getElementById(`request-${requestId}`).remove();
            showNotification("✅ Request cancelled successfully.");
        } else {
            showNotification(`Error cancelling request, try again later ${data.error}`);
        }
    })
    .catch((error) => {
        console.error("Error cancelling request:", error);
        showNotification("Error cancelling request, please try again later.");
    });
}

// Managing a donor request by letting it get accepted or rejected.
// pass the request id and action parameters into the function to identify and manage the right request. The action paramter is basically
// the accept or reject option, which gets called depending on which button is clicked
function handleRequest(requestId, action) {
    fetch(`/api/manage_donor_request/${requestId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ request_id: requestId, action: action }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification("There was an Error: " + data.error);
        } else {
            showNotification(`✅ Request ${action}ed successfully!`);
            loadPendingRequests(); // refresh the list (func call, defined below)
        }
    })
    .catch(error => {
        console.error("Error handling request:", error);
        showNotification("Something went wrong. Try again later.");
    });
}


// Fetch and display pending requests, displayes incoming pending requests and outgoing requests made to other users.
function loadPendingRequests() {
    fetch(`/api/get_requests/`)
        .then(response => response.json())
        .then(data => {
            const incomingList = document.getElementById("incomingRequestsList");
            const outgoingList = document.getElementById("outgoingRequestsList");
            const noIncomingMessage = document.getElementById("noIncomingRequests");

            // if the incoming list div is empty, or no outgoing list div, then return and stop.
            if (!incomingList || !outgoingList) return;

            // clear current content
            incomingList.innerHTML = "";
            outgoingList.innerHTML = "";

            // by defualt the variables for both type of requests will be false because we will dynamically render them
            let hasIncoming = false;
            let hasOutgoing = false;

            // iterate through requests and classify them
            data.requests.forEach(request => {
                const item = document.createElement("li");
                item.className = "list-group-item d-flex justify-content-between align-items-center";

                if (request.is_incoming) {
                    // incoming request (Accept/Reject), with the parameters being, the username and bloodtype of the person who requested it
                    hasIncoming = true;
                    item.innerHTML = `
                        <span>
                            Request from: <strong>${request.requester_username}</strong>
                            (Blood Type: ${request.blood_type_needed})
                        </span>
                        <div>
                            <button class="btn btn-success btn-sm accept-btn" data-request-id="${request.id}">Accept</button>
                            <button class="btn btn-danger btn-sm reject-btn" data-request-id="${request.id}">Reject</button>
                        </div>
                    `;
                    incomingList.appendChild(item);
                } else {
                    // outgoing request (Cancel), the cancel button, created in HTML and the button containts the data, which is the request_id
                    hasOutgoing = true;
                    item.innerHTML = `
                        Request to: <strong>${request.recipient_username}</strong>
                        (Blood Type: ${request.blood_type_needed})
                        <button class="btn btn-danger btn-sm cancel-request" data-request-id="${request.id}">
                            Cancel
                        </button>
                    `;
                    outgoingList.appendChild(item); // append the updated outgoing list to the DOM
                }
            });

            // show "No incoming requests" if empty
            if (!hasIncoming) {
                incomingList.innerHTML = `<li class="list-group-item text-muted">No incoming requests.</li>`;
            }

            // attach event listeners for accept/reject, to detect when the respective buttons are clicked
            document.querySelectorAll(".accept-btn").forEach(button => {
                button.addEventListener("click", () => handleRequest(button.dataset.requestId, "accept"));
            });

            document.querySelectorAll(".reject-btn").forEach(button => {
                button.addEventListener("click", () => handleRequest(button.dataset.requestId, "reject"));
            });

            // attach event listeners for cancel, to detect when the cancel button is ckicked, also call the confirm cancel method in JS for confirmation
            document.querySelectorAll(".cancel-request").forEach(button => {
                button.addEventListener("click", () => confirmCancel(button.dataset.requestId));
            });
        })
        .catch(error => console.error("Error fetching requests:", error));
}

// Function: Fetch Donor Matches (Enhanced with Request Button), this runs the match_donots function in views.py and fetches the matches automatically
// so that the user on the user_profile.html can automatically only see the people they should send the requests to.
function setupMatchDonors() {
    const matchesSection = document.getElementById("matchedDonorsSection");
    const matchesList = document.getElementById("matchesList");

    if (!matchesSection || !matchesList) return; // ensure matches section exists

    fetch("/api/match_donors/")
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch donor matches.");
            return response.json();
        })
        .then(data => {
            // handle API errors
            if (data.error) {
                matchesList.innerHTML = `<li class="text-danger">${data.error}</li>`;
                return;
            }

            // if no matches are found (for whatever reason), return an html list tag(because that section and contents therein as displayed as lists)
            //  that says matches were not found
            if (data.matches.length === 0) {
                matchesList.innerHTML = `<li class="text-muted">No compatible donors found.</li>`;
                return;
            }

            // populate donor list dynamically, we want to show the list of matched donors, and only their imp info for privacy reasons
            // this means the location is hidden for each matched user, if not accepted. else, if the matched user is someone the current logged in user,
            // has accepted a request from, then show locaiton, use the ternary if else operator
            // then show the request donation button
            matchesList.innerHTML = "";
            data.matches.forEach(donor => {
                const donorItem = document.createElement("li");
                donorItem.className = "list-group-item d-flex justify-content-between align-items-center";

                donorItem.innerHTML = `
                    <div>
                        <strong><a href="/user/${donor.id}/profile/">${donor.username}</a></strong>
                        (${donor.blood_type})<br>
                        📧 Email: <a href="mailto:${donor.email}">${donor.email}</a><br>
                        📍 Location: ${donor.is_accepted ? donor.location : "Hidden until accepted"}
                    </div>
                    <button class="btn btn-sm btn-danger request-btn" data-donor-id="${donor.id}">
                        Request Donation
                    </button>
                `;

                matchesList.appendChild(donorItem); // update the matches list div
            });

            // attach event listeners to all request buttons, call createDonationRequest function on the donorId(in models.py)
            document.querySelectorAll(".request-btn").forEach(button => {
                button.addEventListener("click", (e) => {
                    const donorId = e.target.getAttribute("data-donor-id");
                    createDonationRequest(donorId);
                });
            });
        })
        .catch(error => {
            console.error("Error fetching donor matches:", error);
            matchesList.innerHTML = `<li class="text-danger">Error loading matches. Please try again later.</li>`;
        });
}


// Function: Toggle Matches Section, this function sets up event listeners attached to the  "hide matches" button, changing the buttons innerHTML
// depending on if its clicked. The matches are shown by default, when the button is clicked, it hides the matchedDonorsSection and the button text
// changes to "show matches"
function setupToggleMatches() {
    const pendingRequestsList = document.getElementById("pendingRequestsList");
    const matchedSection = document.getElementById("matchedDonorsSection");
    const toggleBtn = document.getElementById("toggleMatches");

    if (!matchedSection || !toggleBtn) return;

    toggleBtn.addEventListener("click", () => {
        console.log("toggleBtn clicked");

        // using computed style to get actual visibility for the matched section
        const isHidden = window.getComputedStyle(matchedSection).display === "none";
        console.log("isHidden updated", isHidden);

        // toggle section visibility
        matchedSection.style.display = isHidden ? "block" : "none";

        // update button text accordingly
        toggleBtn.textContent = isHidden ? "Hide Matches" : "Show Matches";

        console.log("Section is now:", isHidden ? "Visible" : "Hidden");
    });
}


// create a donation request and send it to the selected donor
function createDonationRequest(donorId) {
    fetch(`/api/create_donor_request/${donorId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showNotification(`there was an error ${data.error}`, 5000);
        } else {
            showNotification("✅ Donation request sent!", 5000);
        }
    })
    .catch(error => {
        console.error("Error creating request:", error);
        showNotification("Something went wrong. Try againlater.", 5000);
    });
}



// Function: Fetch and display donors (only runs on the donor list page), setup the donor cards and lists them in the page, also has pagination setup.
function setupDonorList() {
    console.log("setupDonorList running");

    const donorList = document.getElementById("donorList");

    // exit if the donor list section is not found
    if (!donorList) return;

    // start with first donor
    let counter = 1;

    // load donors 15 at a time
    const quantity = 15;

    // when DOM loads, render the first 15 donors
    document.addEventListener('DOMContentLoaded', fetchDonorList);

    // if scrolled to bottom, load the next 15 posts
    window.onscroll = () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            fetchDonorList();
        }
    };

    // initial call to the fetchDonorList() function to populate donors without filters, function itself is mentioned below
    fetchDonorList();

    // add event listener to the filter form
    const filterForm = document.querySelector("form");
    if (filterForm) {
        filterForm.addEventListener("submit", function (event) {
            event.preventDefault(); // prevent default form submission

            // get form data
            const formData = new FormData(filterForm);
            const bloodType = formData.get("blood_type");
            const country = formData.get("country");

            // reset to 1 so filtered list starts from beginning instead of nothing
            counter = 1

            // fetch filtered donor list
            fetchDonorList(bloodType, country);
        });
    }

    // Function: Fetch donors based on filters and populate the list, contained within setupDonorList()
    function fetchDonorList(bloodType = "", country = "") {

        // set start and end donor numbers, and update counter
        const start = counter;
        const end = start + quantity - 1;
        counter = end + 1;

        // place "&start=${start}&end=${end}" parameters to get the donors within the specified range, in this case it is filters to apply the pagination
        fetch(`/api/donors/?blood_type=${bloodType}&country=${country}&start=${start}&end=${end}`)
            .then(response => {
                if (!response.ok) throw new Error("Failed to fetch donors.");
                return response.json();
            })
            .then(data => {
                // populate the updated donor cards
                if (data.donors.length === 0) {
                    donorList.innerHTML = `<p class="text-muted">No registered donors available.</p>`;
                } else {
                    // edit innerHTML of donorList with donor cards and links to the user profile, along with a request button and other donor info
                    donorList.innerHTML = data.donors.map(donor => `
                        <div class="col-md-4">
                            <div class="card shadow-sm border-0">
                                <div class="card-body">
                                    <h5 class="card-title">${donor.user.username}</h5>
                                    <p class="card-text">
                                        <strong>Blood Type:</strong> ${donor.blood_type}<br>
                                        <strong>Country:</strong> ${donor.country || "Not Provided"}
                                    </p>
                                    <a href="/user/${donor.user.id}/profile/" class="btn btn-danger btn-sm">View Profile</a>
                                    <button class="btn btn-outline-primary btn-sm request-btn"
                                            data-donor-id="${donor.user.id}">
                                        Request Donation
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join("");
                }

                // attach event listeners to "Request Donation" buttons, that calls the previous createDonationRequest() function to send a request
                // to the donorId
                document.querySelectorAll(".request-btn").forEach(button => {
                    button.addEventListener("click", function () {
                        const donorId = this.getAttribute("data-donor-id");
                        console.log("Sending request to donor ID:", donorId);
                        createDonationRequest(donorId);
                    });
                });
            })
            .catch(error => {
                console.error("Error fetching donors:", error);
                donorList.innerHTML = `<p class="text-danger">Error loading donors. Try again later.</p>`;
            });
    }
}

// Function: Fetch and display active donation requests (runs on the requests page)
function setupActiveRequests() {
    console.log("setupActiveRequests running");

    const requestsSection = document.getElementById("donationRequestsSection");
    const requestList = document.getElementById("requestList");
    const requestCountBadge = document.getElementById("requestCountBadge");
    const bloodTypeFilter = document.getElementById("blood_type");
    const countryFilter = document.getElementById("country");
    const filterForm = document.querySelector("form");

    // ensure all necessary elements exist before running, like the requests section, the list, counting badge,
    // and both filters ie, bloodtype and country. If elements not found, return and warn with console.warn
    if (!requestsSection || !requestList || !requestCountBadge || !bloodTypeFilter || !countryFilter) {
        console.warn("Missing one or more required elements for active requests.");
        return;
    }

    // debug each section
    console.log("requestsSection:", requestsSection);
    console.log("requestList:", requestList);
    console.log("requestCountBadge:", requestCountBadge);

    // fetch and populate active donation requests initially by calling the fetchActiveRequests() function
    fetchActiveRequests();

    // listen for form submission to apply filters, and prevent default, then call the filtered results
    filterForm.addEventListener("submit", function (event) {
        event.preventDefault(); // prevent default form submission
        fetchActiveRequests(); // fetch filtered results
    });

    // function to fetch active requests, can be filtered by bloodType and country
    function fetchActiveRequests() {
        const bloodType = bloodTypeFilter.value.trim();
        const country = countryFilter.value.trim();

        // not using a hard-coded url in fetch as the filters apply directly to the url parameters and not like other fetch calls where we dont use
        // variables to explicitly state the url in the fetch statement itself. This is for clarity in fetching the multiple, optional paramteres
        // like blood type and country filters.
        let url = "/api/active-requests/?";
        if (bloodType) url += `blood_type=${encodeURIComponent(bloodType)}&`;
        if (country) url += `country=${encodeURIComponent(country)}`;

        console.log("fetching active requests with filters:", url);

        // throw error if response from the server is not as expected
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error("Failed to fetch active requests.");
                return response.json();
            })
            .then(data => {
                console.log("active requests received:", data);

                // update request count badge, this is the badge that shows the number of active requests
                requestCountBadge.textContent = data.active_requests.length;

                // populate active donation requests and show the details, with a check compatibility button that runs the a compatibility check
                // function
                if (data.active_requests.length === 0) {
                    requestList.innerHTML = `<li class="list-group-item text-muted">No active donation requests.</li>`;
                } else {
                    requestList.innerHTML = data.active_requests.map(request => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <strong>${request.requester_username}</strong> needs <strong>${request.blood_type_needed}</strong>
                            at <em>${request.country && request.country.trim() !== "" ? request.country : "Unknown"}</em>
                            <button class="btn btn-outline-danger btn-sm check-compatibility-btn"
                                data-request-id="${request.id}">
                                Check Compatibility
                            </button>
                            <span class="badge ${request.status === 'Pending' ? 'bg-warning' : 'bg-success'}">
                                ${request.status}
                            </span>
                        </li>
                    `).join("");
                }

                // attach event listeners for "Check Compatibility" buttons
                document.querySelectorAll(".check-compatibility-btn").forEach(button => {
                    button.addEventListener("click", function () {
                        const requestId = this.getAttribute("data-request-id");
                        console.log("Checking compatibility for request ID:", requestId);

                        if (!requestId) {
                            showNotification("Invalid request ID.", 3000);
                            return;
                        }

                        checkCompatibility(requestId);
                    });
                });
            })
            .catch(error => {
                console.error("Error fetching active requests:", error);
                requestList.innerHTML = `<li class="list-group-item text-danger">Error loading requests. Try again later.</li>`;
            });
    }

    // Function: Check Blood Compatibility the check compatibility function that queries the compatibility api on the requestId, and gets the data,
    // specifically the blood types of the recipient and donor (requester, requestee) and checks for compatibility
    function checkCompatibility(requestId) {
        fetch(`/api/check_compatibility/${requestId}/`)
            .then(response => {
                if (!response.ok) throw new Error("Failed to check compatibility.");
                return response.json();
            })
            .then(data => {
                console.log("Compatibility Check Response: ", data);
                if (data.error) {
                    showNotification(`❌ ${data.error}`, 5000);
                    return;
                }

                // showing the correct compatibility result
                if (data.is_compatible) {
                    showNotification(`✅ Compatible: Donor (${data.donor_blood}) can donate to Recipient (${data.recipient_blood}).`, 5000);
                } else {
                    showNotification(`❌ Incompatible: Donor (${data.donor_blood}) cannot donate to Recipient (${data.recipient_blood}).`, 5000);
                }
            })
            .catch(error => {
                console.error("❌ Error checking compatibility:", error);
                showNotification("❌ Error checking compatibility. Try again.", 5000);
            });
    }
}


// function and event listeners for check_copmatibility (this is for the check_compatibility page which ANYONE can access)
function setupCheckCompatibility() {
    console.log("initializing compatibility check");

    // dont run the function if not on the right page
    const compatibilityDataElement = document.getElementById("compatibility-data");
    if (!compatibilityDataElement) return;

    const compatibilityChart = JSON.parse(compatibilityDataElement.textContent);
    const checkBtn = document.getElementById("check-compatibility-btn");
    const resultMsg = document.getElementById("result-message");
    const loadingIndicator = document.getElementById("loading-indicator");

    if (!checkBtn || !resultMsg) return;

    checkBtn.addEventListener("click", () => {
        const donorBlood = document.getElementById("donor_blood").value;
        const recipientBlood = document.getElementById("recipient_blood").value;

        if (!donorBlood || !recipientBlood) {
            showResult("⚠️ Please select both blood types!", "warning");
            return;
        }

        // Show loading spinner and disable button
        loadingIndicator.classList.remove("d-none");
        checkBtn.disabled = true;

        fetch(`/api/check_compatibility/?donor_blood=${encodeURIComponent(donorBlood)}&recipient_blood=${encodeURIComponent(recipientBlood)}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add("d-none");
            checkBtn.disabled = false;


            if (data.error) {
                showResult(`❌ ${data.error}`, "danger");
            } else {
                showResult(
                    data.is_compatible
                        ? `✅ ${donorBlood} is <strong>compatible</strong> with ${recipientBlood}!`
                        : `❌ ${donorBlood} is <strong>not compatible</strong> with ${recipientBlood}.`,
                    data.is_compatible ? "success" : "danger"
                );
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showResult("Error checking compatibility. Please try again.", "danger");
            loadingIndicator.classList.add("d-none");
            checkBtn.disabled = false;
        });
    });

    // function called everytime someone requests a compatibility check and wants the results displayed
    function showResult(message, type) {
        resultMsg.className = `alert alert-${type} text-center`;
        resultMsg.innerHTML = message;
        resultMsg.classList.remove("d-none");
    }
}



// custom bottom notification with reverse progress bar, passing in the message and timeout parameters
function showNotification(message, timeout = 5000) {

    const notificationCard = document.getElementById("notification-card");
    const notificationMessage = document.getElementById("notification-message");
    const notificationProgress = document.getElementById("notification-progress");

    // set message content and show card
    notificationMessage.textContent = message;
    notificationCard.classList.add("show");
    notificationCard.style.display = "flex";

    // start reverse progress animation
    notificationProgress.style.width = "100%";
    setTimeout(() => {
        notificationProgress.style.transition = `width ${timeout}ms linear`;
        notificationProgress.style.width = "0";
    }, 50); // slight delay for smooth start

    // auto hide after timeout
    if (timeout) {
        setTimeout(closeNotification, timeout);
    }
}

// close the notification manually or auto hide
function closeNotification() {
    const notificationCard = document.getElementById("notification-card");
    notificationCard.classList.remove("show");

    // wait for animation to complete before hiding
    setTimeout(() => {
        notificationCard.style.display = "none";
    }, 500); // match transition duration
}

