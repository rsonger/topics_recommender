from uuid import UUID
from pathlib import Path
import joblib

from django.shortcuts import render, redirect
from django.views.generic import CreateView, View
from django.utils.translation import get_language
from django.utils import timezone
from django.apps import apps

from survey_tasks.models import DATResponse, DATWord
from survey_tasks.models import CTTCategory, CTTIdea, CTTResponse

from survey_tasks.dat_models import DATModels

from topics_recommender.models import UserSession, Topic

class RecommenderView(View):
    response_model = apps.get_model("survey_tasks", "RecommenderResponse")
    endpoint_name = "survey_tasks"
    template_name = f"{endpoint_name}/recommender.html"
    num_topics = 3 # number of topics for the user to choose

    def get(self, request, *args, **kwargs):
        # make sure a user is already logged in
        if not request.session.get("id", False):
            return redirect('login')
                
        for n in range(1, self.num_topics+1):
            if not request.session.get('topics',[''] * self.num_topics)[n-1]:
                return redirect('search')

        return render(request, self.template_name) 

    def post(self, request, *args, **kwargs):
        # get the active user session
        user_session_id = self.request.session.get("id")
        if not user_session_id:
            return redirect('login')
        user_session = UserSession.objects.get(id=UUID(user_session_id))

        params = {'user_session': user_session}
        cosine_scores = joblib.load(
            Path("data/cosine_sim_scores_en.joblib")
        )
        
        # build the topic parameters for the database object
        for n in range(1, self.num_topics+1):
            topic = Topic.objects.get(display_name=request.session['topics'][n-1])
            params[f'topic{n}'] = topic
            # build the sim score parameters for the database object
            if n > 1:
                id_a = params[f'topic{n-1}'].id
                id_b = params[f'topic{n}'].id
                params[f'sim_score_{n-1}_{n}'] = cosine_scores[id_a][id_b]
            if n > 2:
                for i in range(n-2, 0, -1):
                    id_a = params[f'topic{n}'].id
                    id_b = params[f'topic{i}'].id
                    params[f'sim_score_{n}_{i}'] = cosine_scores[id_a][id_b]

        # there should be only one response per user session
        response = self.response_model.objects.filter(
            user_session=user_session,
        )
        if len(response) == 0:
            response = self.response_model.objects.create(**params)
        else:
            response = response[0]
            for k in params:
                if k == "user_session":
                    continue
                setattr(response, k, params[k])

            response.save()

        if self.num_topics == 3: # Version 1
            return redirect('dat')
        return redirect('logout') # Version 2

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

        words = {k:v for k,v in request.POST.items() if k[0] == 'w'}
        lang = get_language()

        # check the validity of the words against the DAT model
        dat_model = DATModels().get_model(lang)

        invalid_words = []
        for k,v in words.items():
            if not dat_model.validate(v):
                invalid_words.append(k)
        
        if len(invalid_words) > 0:
            context = words.copy()
            context["invalid"] = invalid_words
            
            return render(request, 'survey_tasks/dat.html', context=context)

        # get the DAT score since all the words are valid
        dat_score = dat_model.dat(words.values())

        # create or update a DB object for this response
        response, created = DATResponse.objects.get_or_create(
            user_session=user_session,
        )
        response.dat_score = dat_score
        # update the timestamp if it already exists
        if not created:
            response.submitted_at = timezone.now()
        response.save()
        # remove any existing words not in this post
        for dw in DATWord.objects.filter(response=response):
            if dw.value not in words.values():
                dw.delete()
        # add words that don't exist yet
        for w in words.values():
            DATWord.objects.get_or_create(
                value=w, 
                language_code=lang, 
                response=response
            )

        return render(request, 'survey_tasks/ctt.html')


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
        
        # create or update a DB object for this response
        response, created = CTTResponse.objects.get_or_create(
            user_session=user_session,
        )
        if not created:
            response.submitted_at = timezone.now()
            response.save()
        for c in CTTCategory.objects.filter(response=response):
            if c.title not in params.values():
                c.delete()
        # check each of the 5 category titles and grouping params
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

        return redirect('logout')