from django.shortcuts import render
import markdown2
import secrets
from . import util
from django import forms
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown

class NewEntriesForm(forms.Form):
    title = forms.CharField(label="Entry title", widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })



def data(request, entry):
    markdowner = Markdown()
    entrydata = util.get_entry(entry)
    if entrydata is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        return render(request, "encyclopedia/entries.html", {
            "entry": markdowner.convert(entrydata),
            "entryTitle": entry
        })

def newEntry(request):
    if request.method == "POST":
        form = NewEntriesForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/newentries.html", {
                "form": form,
                "existing": True,
                "entry": title
                })
        else:
            return render(request, "encyclopedia/newentries.html", {
            "form": form,
            "existing": False
            })
    else:
        return render(request,"encyclopedia/newentries.html", {
            "form": NewEntriesForm(),
            "existing": False
        })

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        form = NewEntriesForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newentries.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entryTitle": form.fields["title"].initial
        })


def search(request):
    query = request.GET.get('q','')
    if (util.get_entry(query) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': query}))

    else:
       subStringEntries = []
    for entry in util.list_entries():
            if query.upper() in entry.upper():
                subStringEntries.append(entry)

                return render(request, "encyclopedia/index.html", {
                 "entries": subStringEntries,
                 "search": True,
                   "query": query
                                  })


def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': randomEntry}))
