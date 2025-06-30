# Blood Compatibility & Availability

#### Video Demo:  [Youtube Link](https://youtu.be/nvnZ8tmijI0)

## Description

- This project is my `Proof-of-Concept` project since I have wanted to focus on a web-based application made primarily with **Django, React, JavaScript and dependent visualization frameworks like Three.js and D3.js, HTML, CSS and Bootstrap**. It has been containserised using the Docker for ease of use and consistency in performance.

### **Technologies Used**

#### **Backend:**
- Django
- Python
- SQL
- Docker
- Unittest
- Selenium

#### **Frontend:**
- JavaScript
- JSX
- CSS
- HTML
- jQuery
- React
- Ajax
- Django Templating Language

#### **CDN Dependencies:**
- Bootstrap
- Three.js
- D3.js
- React (React-DOM, React-Babel, React-Main)

#### **External APIs:**
- HERE Maps API
- HERE Autocomplete API
- HERE UI API
- HERE Maps Vector Topography API

#### **RESTful APIs:**
- Proprietary backend APIs enabling Ajax functionality with **12 endpoints** and corresponding REST APIs.
- Django REST Framework (DRF) APIs for authentication and validation.


---

## <ins>The Concept and Inspiration</ins>

The idea behind this project was to build something meaningful ie, an application that merges biotechnology with software development in a way that is educational, practical, and potentially life-saving. I dedicated over six weeks to full-time development of this project, consistently tackling complex problems head-on and embracing the learning curve with the goal of creating a maybe overreaching but *potentially* useful product.

With a background in biotechnology and a growing passion for software development, I wanted to create a web-based application that could visualize and explain complex biological concepts while also serving a real-world use case. The result was a Django-based project comprising two main applications: **Compatibility**, which manages user interactions and blood compatibility, and **Inheritance**, which handles data visualizations and education around blood type inheritance and transfusion logic.

A major inspiration was the story of [James Harrison](https://www.bbc.com/news/articles/c5y4xqe60gyo), an Australian man who donated blood plasma and saved over 2 million lives. His selflessness brought attention to the critical need for blood and plasma donations worldwide. This sparked the idea of building a **volunteer-driven**, open source platform that could anonymize user-reported blood availability and compatibility information. So, an app built not just to function, but to inform, connect, and *potentially* save lives.

It occoured to me that a concept of a **free, open source application where blood availability was anonimised by the users and for the users**, and the application also encompassed **real-time data** of how much, of a certain blood type was available, in a given or chosen place, was not really a thing after scouring the internet for research. I'm sure there are good reasons for it but with the right security checks in place it can be done. Be it city, country or state, nobody should have their lives threatened just because blood availability is low or someone doesn't know whether there is any blood type available within their region without consulting the hospital because that can be a long and tedious process depending on the country, while the users themselves still remained anonymous, unless they decided not to remain anonymous.
I also wanted **real-time compatibility checks and an educative visualization** aspect of compatibility for transfusions all in one place. Thats when I decided I wanted to approach this simple idea that would do most of what I wanted to achieve.

My goal wasn’t to build just another app, it was to create something that, if scaled properly, could make a meaningful impact. Even if it saves just **one** life, it will have served its purpose.

---

### <ins>Usage Note</ins>

This application is a **proof of concept** and is not intended to replace official or medical-grade blood donation platforms. It serves as a community-driven platform where users can:

* Anonymously register their blood type and approximate region.
* Mark themselves available or unavailable for donations.
* Send and receive donation requests (with mutual consent).
* Learn about blood compatibility and inheritance via interactive tools.

Exact user locations are never stored, only general administrative boundaries (city, state, country). Location data is used solely to show blood availability trends at a regional level. Users can remain fully anonymous or choose to engage further. Any interactions for donations are *meant* to lead to **official procedures** via hospitals or blood donation drives.

---

## <ins>Why is it special?</ins>

### General Idea

The application consists of two Django modules:

* **Compatibility**: Manages user interactions, blood type compatibility logic, location-based data, and availability.
* **Inheritance**: Provides interactive educational tools, including blood cell visualizers, inheritance models, and allele mapping using JavaScript libraries.

It acts as a **multi-purpose platform** that combines:

* Real-time data visualization
* Biological education
* User interaction and compatibility logic

This platform is not a social network nor a standard web app, it’s a **hybrid of education, awareness, and real-time blood availability**, aiming to lower the barrier to participation in voluntary blood donation.

### Uniqueness

Unlike many applications, this one isn’t purely functional, it’s mission-driven. Blood donation awareness is still lacking, and many people are unaware of even the basics of blood compatibility or what makes their own blood unique.

This project seeks to bridge that knowledge gap, while also reducing psychological and logistical barriers to donating. It approaches the problem holistically: by making blood science interactive, the aim is to make the topic **less intimidating and more inviting**, encouraging informed voluntary participation.

Through a user-first design, anonymity options, visual learning, and real-time matching logic, the platform becomes **both a tool and a teacher**.

### Challenges and Complexities

Building this platform required learning and integrating several technologies:

* **Three.js** and **D3.js** for rendering 3D blood cells and inheritance graphs.
* **HERE Maps API** for location visualization, without compromising user privacy.
* **Django REST Framework (DRF)** to create custom APIs for efficient frontend-backend communication.

One major challenge was enabling **location-based search and visualization** without ever storing or displaying user coordinates. This meant utilizing HERE’s Autocomplete API to derive city/state/country data **without persisting raw GPS data**. Only default administrative boundary coordinates were used to render visual bubbles on the map, respecting privacy while enabling functionality.

Due to a **strict API rate limit** (5 calls/sec, 1000/day on the free tier), I had to implement intelligent **rate-limiting and caching strategies**. This included timeout mechanisms, input debouncing, and API call batching to stay within limits.

The **Inheritance module** presented another set of challenges. Translating a Python-based inheritance algorithm into JavaScript (I'm not the best at JS), and visualizing it using D3.js and Three.js, required intensive research, debugging, and adaptation especially when dealing with biological data representation like antigens, alleles, and Rh factors.

Some features (like password reset via email or notification systems) were deferred (but coming soon, probably...) due to constraints like needing a verified domain and premium APIs. However, the core experience and architecture were completed as planned.

### Summary

This project brought together software engineering, design thinking, and scientific visualization into a unique and cohesive platform. It blends a practical tool with a strong educational and social purpose. While currently a **proof of concept**, it lays the foundation for a fully deployable, scalable system that could genuinely make a difference in the area of blood donation awareness and accessibility.

---


## Todo's and WIP implementations:-

#### Dev goals for significant but approachable changes
- ML based matchmaking with optimal donor recommendations based on things like proximity, compatibility and availability patterns. Could also predict regional shortages based on chronological data (if I find a viable dataset)
- Notification system and not just in app popups (only ajax notifs are setup as of now)
- Multi-Language support -> Django's `i18n` framework
- Maybe an offline mode?
- In app messaging system (E2E Encryption for GDPR compliance and ISO stuff)
- 2FA 

#### Scaling ideas and commercialising
- Badges for number of donations
- streaks? or perhaps an "impact tracker" ie, `you have helped n number of people`
- A blood drive map with some community driven coordination, like notifications blood drive events and regions in particular need
- Emergency mode / SOS broadcast signal for non blood-donation related things as well?
- Donor health tracker, hemoglobin lvls last donation etc



## Table of Contents

1. Features
2. External API and CDN information
3. Internal / RESTFUL API information
4. Inheritance Algorithm Visualisation and Blood Cell 3d visualisation
5. Installation
6. Usage


### 1. <ins>Features</ins>

The entire application is made in **Django**, and the main boiler plate stuff is still **JavaScript**, **HTML** and **CSS**, and **React** for state control-and-manipulation. React is only used in the Inheritance application as the Inheritance application actually had a use case to use React and I didn't see a need for using React in the Compatibility app. It also uses 3D visualisation and algorithm visualisation both take user inputs and dynamically change depending on the user inputs.

<ins>The application has a full scope of operations ie, every aspect of the this application can handle both front end and backend logic and complete database operation for multiple users. The features, main functions and important files are as follows:</ins>

### 1.1 <ins>Compatibility</ins>

#### <ins>Overall Functionality</ins>

The **Blood Compatibility App** allows users to register as **donors** by providing their blood type and other relevant information. Upon signing up, users gain full access to the application's features.

#### <ins>User Flow</ins>

1. **Registration & Navigation**
   - After signing up/registration, the user is redirected to the **index page**, where they can explore all functionalities through the **navigation bar**.

2. **Key Features**
   - **Map View:** Users can access the **HERE Maps-based page**, displaying registered donors in various locations. The map bubbles themselves can be clicked on to display an information box which shows simple details like the donor count, blood type and number of the specific blood type(s). Which would be summarised as **"There is 1 Donor with blood type O+ in Frankfurt"**.
   - **User Profile Page (`user_profile.html`)**
     - View personal profile details.
     - Send requests to compatible donors, automatically suggested using the **Compatibility API**.
     - Manage requests:
       - **Cancel outgoing requests**
       - **Accept/reject incoming requests**
     - Edit or delete profile (Note: **Email is non-editable for security reasons**).
       - To change the email, users must **delete their profile and re-register**.

3. **Active Requests Page**
   - View **all active blood requests**, displayed as **cards** with details.
   - Each request includes a **compatibility check button**, which runs the **same compatibility function** (albeit as an api view) and provides a message indicating compatibility status.

4. **Finding Donors & Hospitals**
   - Users can:
     - Visit the nearest **hospital** or **blood drive event**, based on donor data on the **HERE Maps API**.
     - Use the **country filter** to find compatible donors within a specific location.
     - If no hospital or blood drive is available, users can send a **direct request** to a donor.

5. **Privacy Considerations**
   - Only the **recipient's country and email** are visible to ensure privacy and security. The email is visible be default for now as there is no way to notify a user unless they sign in regularly and in emergency situations, it can make all the difference to save a potential life. The user can always block a suspected spammer or just not reply. The difference is the first contact/notification is always present. It is upto the users to decide how they want to proceed.
   - Blood donation requires mutual agreement between the donor and the recipient. That and other security and explicit usage disclaimers have been made abundantly clear in the **about** page.


### 1.2 <ins>Inheritance</ins>

- **<ins>Overall functionality:-</ins>**
 - **Educational Section:** The **Blood Inheritance App**, powered by **React**, provides interactive visualizations to understand blood compatibility and inheritance patterns. These visualisations use **Three.js** and **D3.js**.


### 2. <ins>External API and CDN Information</ins>

#### 2.1 <ins>CDN Usage</ins>

The project relies on several **CDN libraries** for styling, visualisation, and functionality:

##### **Styling & UI Components**
- **[Bootstrap](https://getbootstrap.com/)** – Used for layout, buttons, navbar, accordions, padding, scrollbars, and hover effects.
- **Bootstrap Icons** – For the icons.

##### **Data Visualization & Interactive Elements**
- **[React](https://reactjs.org/)** (via CDN) – Manages UI components in the inheritance app.
- **[Three.js](https://threejs.org/)** – Enables 3D blood cell visualizations.
 - **[Three.js animation sample](https://github.com/mrdoob/three.js/blob/master/examples/webgl_morphtargets.html)** 3D model source code
- **[D3.js](https://d3js.org/)** – Supports the interactive Inheritance Algorithm rendering.
- **Import maps for Three.js** – Specifies module locations for efficient loading according to the Three.js docs.

##### **HERE Maps API (For Compatibility App)**
- **[HERE Location Services](https://www.here.com/docs/category/location-services)** used to display donor locations on the interactive map.
- Includes services for map rendering, UI interactions, and event handling. Used mainly also in the ```user_profile.html```, to keep updated locations consistent and reliable using HERE's own database and subsequently, (because the application itself uses HERE's location capture to store the same location string, albeit split into city/state/country) the application's own database is a also consistent, preventing any discrepencies in data.

```html
<!-- HERE Maps API -->
<script src="https://js.api.here.com/v3/3.1/mapsjs-core.js"></script>
<script src="https://js.api.here.com/v3/3.1/mapsjs-service.js"></script>
<script src="https://js.api.here.com/v3/3.1/mapsjs-ui.js"></script>
<script src="https://js.api.here.com/v3/3.1/mapsjs-mapevents.js"></script>
<link rel="stylesheet" href="https://js.api.here.com/v3/3.1/mapsjs-ui.css" />
```

### 3. <ins>Internal RESTful API Endpoints</ins>

- Since the application exposes several **Django REST framework based** API endpoints for handling user interactions, below is a detailed view at what each url does:

#### **Authentication & User Management**
```python
path("login/", views.login_view, name="login"),
path("logout/", views.logout_view, name="logout"),
path("register/", views.register, name="register"),
path("user/<int:user_id>/profile/", views.profile_page, name="user_profile"),
path("api/edit_profile/", views.edit_profile, name="edit_profile"),
```

#### **Blood Compatibility API**
- Allows users to manually check blood compatibility or automatically match donors.

```python
path("api/check_compatibility/", views.check_compatibility, name="check_compatibility"),
path("api/check_compatibility/<int:request_id>/", views.check_compatibility, name="check_compatibility"),
```

#### **Donor Management & Requests**
```python
path("donors/", views.donor_list_page, name="donor_list"),
path("api/donors/", views.donor_list_api, name="donor_list_api"),
path("api/match_donors/", views.match_donors, name="match_donors"),
path("api/create_donor_request/<int:recipient_id>", views.create_donor_request, name="create_request"),
path("api/manage_donor_request/<int:request_id>", views.manage_donor_request, name="manage_request"),
```

#### **Active Requests & Get Requests**
```python
path("active-requests/", views.active_requests_page, name="active_requests"),
path("api/active-requests/", views.active_requests_api, name="active_requests_api"),
path("api/get_requests/", views.get_requests, name="get_requests"),
```

#### **Request Management**
```python
path("accept_request/<int:request_id>/", views.accept_request, name="accept_request"),
path("cancel_request/<int:request_id>/", views.cancel_request, name="cancel_request"),
path("api/get_outgoing_requests/", views.get_outgoing_requests, name="outgoing_requests"),
```

### 4. <ins>Algorithm Visualisation and Concept interaction/visualization</ins>

- I wanted to have complex algorithm visualisation functionality built into the **Inheritance** application for the website as this not only helps me practice what I have learnt but it also makes me push to learn more intricate details of **JavaScript** and it's famed **"extensive"** libraries. Generally I am quite fond of making visualisations, I have done so at a lower level, before but I need more practice and experience to make truly exceptional data-driven visualisations.

- It was definitely challenging and frustrating making these visualisations but they look informative and I am definitely proud of the perfectly imperfect animations and visualisations I managed to make.

### 5. <ins>Installation</ins>
1. download `capstone` folder and open in your IDE
2. navigate to project directory `cd capstone`
3. install and the docker and open ` docker run `
4. watch the application run, and use it by  `ctrl left click` on the IP and port that appear in the terminal, usually ends with `8000` for local hosting.

### 6. <ins>Usage</ins>
- navigate to the newly opened port `8000` in your web browser (your IDE will likely prompt you to open the link)
- interact with the application and follow its guidance

### Notes:

- The `docker` should run everything automatically after installing the project, I made sure to test it, but it may fail if the right port is not created as Django's default is `8000` but on some systems it may prompt **two** error messages regarding **``CSRF_TRUSTED_ORIGINS``**, if that happens check `settings.py` and add - `ALLOWED_HOSTS = []` and/or `CSRF_TRUSTED_ORIGINS = ['https://localhost:8000']` , relaunch the application manually by running `python manage.py runserver` and it should run just fine.

- The main source of educational information and medical information, such as the compatibility chart, and what blood is and how it functions is [Canadian Blood Services](https://www.blood.ca/en).

- The source where I learned about blood cells and what makes up blood (components like plasma, rbc, wbc etc) as a whole to make the **3D visualisations**, comes from [Britannica](https://www.britannica.com/science/red-blood-cell)

- I made sure to stay accurate to the scientific and biological information from the sources cited above, as much as possible. It **has** to be accurate because I understand that this is a serious matter and misinformation even without mal-intent is dangerous. As such, the **about** page of the application *clearly* states the intended use and precautions to take when going beyond the scope of the application ie, after the first contact has been made between two people. There is no option for a profile photo, or anything else that detracts from the primary intended use case of being a volunteer oriented, open source, Blood Compatibility & Availability application. This is inline with the goal to do away with distractions and non-essential features.
