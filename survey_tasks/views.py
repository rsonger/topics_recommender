from uuid import UUID

from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.utils.translation import get_language

from survey_tasks.models import DATResponse, DATWord
from survey_tasks.models import CTTCategory, CTTIdea, CTTResponse

from topics_recommender.models import UserSession

class DATView(CreateView):

    def get(self, request, *args, **kwargs):
        # make sure a user is already logged in
        if not request.session.get("id", False):
            return redirect('login')
        # otherwise, proceed to render the form
        return render(request, 'survey_tasks/dat.html')

    def post(self, request, *args, **kwargs):
        # get the active user session
        user_session_id = self.request.session.get("id")
        if not user_session_id:
            return redirect('login')
        user_session = UserSession.objects.get(id=UUID(user_session_id))

        params = {k:v for k,v in request.POST.items() if k[0] == 'w'}
        lang = get_language()

        response = DATResponse(user_session=user_session)
        response.save()
        for w in params.values():
            word = DATWord(value=w, language_code=lang, response=response)
            word.save()

        return render(request, 'survey_tasks/dat.html')


class CTTView(CreateView):

    def get(self, request, *args, **kwargs):
        # make sure a user is already logged in
        if not request.session.get("id", False):
            return redirect('login')
        # otherwise, proceed to render the form
        return render(request, 'survey_tasks/ctt.html')

    def post(self, request, *args, **kwargs):
        # get the active user session
        user_session_id = self.request.session.get("id")
        if not user_session_id:
            return redirect('login')
        user_session = UserSession.objects.get(id=UUID(user_session_id))

        params = {
            k:v for k,v in request.POST.items() 
            if k.find("title") > -1 or k.find("cat") > -1
        }
        lang = get_language()
        
        response = CTTResponse(user_session=user_session)
        response.save()
        # check each of the 5 category titles and grouping
        for i in range(1,6):
            title, group = params[f"title{i}"], params[f"cat{i}"]
            if title or group:
                # create a category record
                category = CTTCategory(
                    title=title, 
                    language_code=lang,
                    response=response
                )
                category.save()

                # collect the grouped ideas and add them to the category
                idea_nums = group.split('.')
                ideas = [CTTIdea.objects.get(id=n) for n in idea_nums if n]
                category.ideas.add(*ideas)

        return render(request, 'survey_tasks/ctt.html')