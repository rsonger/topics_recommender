from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.utils.translation import get_language

from survey_tasks.models import DATResponse, DATWord

class DATView(CreateView):

    def get(self, request, *args, **kwargs):
        # make sure a user is already logged in
        if not request.session.get("id", False):
            return redirect('login')
        # otherwise, proceed to render the form
        return render(request, 'survey_tasks/dat.html')

    def post(self, request, *args, **kwargs):
        if not request.session.get("id", False):
            return redirect('login')

        params = {k:v for k,v in request.POST.items() if k[0] == 'w'}
        lang = get_language()

        response = DATResponse()
        response.save()
        for w in params.values():
            word = DATWord(value=w, language_code=lang, response=response)
            word.save()

        return render(request, 'survey_tasks/dat.html')
