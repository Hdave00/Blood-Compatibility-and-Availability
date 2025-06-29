from django.shortcuts import render


# This application will be built along with the login functionality from compatibility application
# it wll only handle the display of the blood group inheritance visualization using d3.js or three.js
# and it will have some educational resources about blood groups and types and how they work.

def inheritance_page(request):
    """ renders the interactive html page for visualising the inheritance algorithm
     Note: It also uses react to render/change two other components and their states, one is an educational/awareness html div and the other is
       a 3d visualisation of a blood cell and its antigens.
         The root container/app for the React component is the inheritance app, which is shown by default when the page renders.  """

    return render(request, "inheritance/inheritance.html")
