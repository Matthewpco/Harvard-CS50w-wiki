from django.shortcuts import render, redirect
from django.http import Http404
from django import forms
from . import util
import markdown2, random


# Django forms for new page and edit page
class NewPageForm(forms.Form):
    title = forms.CharField(label='Title')
    content = forms.CharField(label='Content', widget=forms.Textarea)

class EditPageForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea)

# Routes to home page and shows all entries
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Handles a search given a request
def search(request):
    # Get the query and case match
    query = request.GET.get('q').lower()
    # Get entries and case match
    entries = [entry.lower() for entry in util.list_entries()]
    partial_matches = []
    # If search request in entries redirect to that entry
    if query in entries:
        return redirect('entry', page_url=query)
    # Check for partial matches and append
    for entry in entries:
        if query in entry:
            partial_matches.append(entry)
    # Render any partial matches with search template       
    return render(request, "encyclopedia/search.html", {
        "search_results" : partial_matches
    })


# Takes page_url input to route to appropriate page
def entry(request, page_url):
    
    page_list = util.list_entries()

    # Change both url and list items to lowercase for case matching issues
    lowercase_page_url = page_url.lower()
    lowercase_page_list = [item.lower() for item in page_list]
    
    # Check if page is in the list
    if lowercase_page_url not in lowercase_page_list:
        raise Http404("Not found")

    # Get data markdown data from entry
    page_entry = util.get_entry(page_url)

    # Process data from markdown to html
    converted_html = markdown2.markdown(page_entry)

    # Render entry template and pass data
    return render(request, "encyclopedia/entry.html", {      
        "page_url" : page_url,
        "entry_html" : converted_html,
        "page_list" : page_list
    })

def add_new_entry(request):

    page_list = util.list_entries()

    # Check if form has been submitted
    if request.method == "POST":

        # Get submitted form
        form = NewPageForm(request.POST)

        # Check if form is valid
        if form.is_valid():

            # Assign the cleaned form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if form data is already in entries and give an error
            if title in page_list:
                form.add_error('title', 'This title already exists.')
                return render(request, "encyclopedia/new.html", {
                    "form": form
                })
            # Form data does not already exist so save entry and redirect
            else:
                util.save_entry(title,content)
                return redirect('entry', page_url=title)
        # If form is not valid handle error and re-render form
        else:
            form.add_error(None, 'Form is not valid.')
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
    # Render the new template on get request and pass Django form
    return render(request, "encyclopedia/new.html", {
        "form": NewPageForm()
    })

# Handle editing an existing entry
def edit_entry(request, page_url):

    # Get data from entry
    page_entry = util.get_entry(page_url)

    # Process data from markdown to html
    converted_html = markdown2.markdown(page_entry)
    
    # Check if form has been submitted
    if request.method == "POST":

        # Get form
        form = EditPageForm(request.POST)

        # Get form edit entry data
        edit_entry = request.POST.get('edit_entry')

        # If data exists
        if edit_entry:
            # Load the entry content 
            form = EditPageForm(initial={'content': converted_html})

            # Route to edit template
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "page_url": page_url
            })
        
        # Check if form is valid
        if form.is_valid():

            # Get the form data
            title = page_url
            content = form.cleaned_data["content"]

            # Save new form data to entry and redirect to entry page
            util.save_entry(title,content)
            return redirect('entry', page_url=title)
        # Invalid form returns an error and reloads the page with the given form content
        else:
            form.add_error(None, 'Form is not valid.')
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
    # Render edit page form on get request
    return render(request, "encyclopedia/edit.html", {
        "form": EditPageForm(),
        "page_url" : page_url,
    })

def random_page(request):

    page_list = util.list_entries()

    # Get a random entry
    random_page = random.choice(page_list)

    # Get data markdown data from entry
    page_entry = util.get_entry(random_page)

    # Process data from markdown to html
    converted_html = markdown2.markdown(page_entry)

    # Render entry template and pass data
    return render(request, "encyclopedia/entry.html", {      
        "page_url" : random_page,
        "entry_html" : converted_html,
        "page_list" : page_list
    })