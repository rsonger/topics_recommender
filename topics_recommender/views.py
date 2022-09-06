# standard imports
import ast
import random
from uuid import UUID

# Django imports
from django.views.generic import View, ListView, CreateView, RedirectView
from django.utils import timezone
from django.utils.translation import get_language
from django.shortcuts import redirect, render

# local imports
from ml_api.models import MLAlgorithm
from ml_api.models import MLRequest
from topics_recommender.models import Topic, UserSession
from topics_recommender.forms import LoginForm
from Topics_RS.wsgi import registry

class TopicsListView(ListView):
    """A single list of all the topics in the database."""
    model = Topic
    template_name = "topics_recommender/index.html"

class LoginView(CreateView):

    def get(self, request, *args, **kwargs):
        # make sure a session is not already running
        if request.session.get("id"):
            return redirect('search')
        # otherwise, proceed to login
        context = {'form': LoginForm()}
        return render(request, 'topics_recommender/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            u_session = form.save()
            request.session["id"] = u_session.id.hex
            if u_session.name:
                request.session["name"] = u_session.name
            return redirect('start')
        context = {'form': form}
        return render(request, 'topics_recommender/login.html', context)

class LogoutView(RedirectView):
    pattern_name = "end"

    def get_redirect_url(self, *args, **kwargs):
        session_id = self.request.session.get("id", False)
        if session_id:
            session_id = UUID(session_id)
            if UserSession.objects.filter(id=session_id).exists():
                session_object = UserSession.objects.get(id=session_id)
                session_object.finished_at = timezone.now()
                session_object.save()
            self.request.session.flush()
        return super().get_redirect_url(*args, **kwargs)

class SearchView(ListView):
    """A search page and list of results using the recommender function."""
    model = Topic
    endpoint_name = "topics_recommender"
    template_name = f"{endpoint_name}/search.html"
    context_object_name = "topics_ranking"

    def _handle_chosen_topic(self, topic):
        if not self.request.session.get('topic1'):
            self.request.session['topic1'] = topic
        elif not self.request.session.get('topic2'):
            self.request.session['topic2'] = topic
        elif not self.request.session.get('topic3'):
            self.request.session['topic3'] = topic

    def setup(self, request, *args, **kwargs) -> None:
        self._start_time = timezone.now()
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # redirect to the login page if the session has not been initialized
        if not request.session.get('id', False):
            return redirect('login')
        # otherwise, proceed
        return super().get(request, *args, **kwargs)

    def get_queryset(self): 
        # get the active user session
        user_session_id = UUID(self.request.session["id"])
        user_session = UserSession.objects.get(id=user_session_id)

        # get the query parameters
        query = self.request.GET.get('q')
        if not query or len(query) == 0:
            return Topic.objects.none()
        featured = self.request.GET.get('f')
        top_ranks = self.request.GET.get('r')
        if top_ranks:
            try:
                top_ranks = int(top_ranks)
            except:
                top_ranks = 10
        else:
            top_ranks = 10
        previous_request = self.request.GET.get('rid')
        previous_request_rank = self.request.GET.get('i')
        topic_chosen = self.request.GET.get('c')
        topic_removed = False
        if self.request.GET.get('t1') is not None:
            topic_removed = 'topic1'
        if self.request.GET.get('t2') is not None:
            topic_removed = 'topic2'
        if self.request.GET.get('t3') is not None:
            topic_removed = 'topic3'
        params = {
            "q": query, 
            "f": featured, 
            "r": top_ranks,
            "l": get_language()
        }

        # handle the adding and removing of chosen topics to the session
        if topic_chosen:
            self._handle_chosen_topic(query)
        if topic_removed:
            self.request.session[topic_removed] = ''

        # load the recommender algorithm for this endpoint
        db_algorithms = MLAlgorithm.objects.filter(
            parent_endpoint__name=self.endpoint_name,
            active=True
        )

        # get an algorithm to use for creating the search ranking
        algo_index = 0
        if len(db_algorithms) == 0:
            raise Exception(f"CONFIGURATION ERROR: No active algorithms for endpoint {self.endpoint_name}.")
        elif len(db_algorithms) > 1:
            # get a random algorithm that will always be the same for this user session
            random.seed(user_session_id.hex)
            algo_index = round(random.random() * (len(db_algorithms) - 1))
        algorithm_object = registry.get_algorithm(db_algorithms[algo_index].id)
        if algorithm_object is None:
            raise Exception(f"CONFIGURATION ERROR: No corresponding algorithm in the registry for {db_algorithms[0]}")

        # get the top 10 ranking of recommended topics for the query
        lookup = Topic.objects.filter(display_name__iexact=query)
        if len(lookup) == 0:
            return lookup
        else:
            lookup = lookup[0]

        prediction = algorithm_object.make_ranking(
            lookup.name, 
            lookup.id, 
            top_ranks,
            params["l"]
        )

        if prediction["request_log"]["status"] == "Error":
            # Log the error in a MLRequest object
            ml_request = MLRequest(
                input_data=str(params),
                response=prediction["request_log"]["status"],
                full_response=prediction["request_log"],
                ranking="",
                feedback="",
                parent_mlalgorithm=db_algorithms[0],
                user_session=user_session
            )
            ml_request.save()

            self.request_id = ml_request.id

            raise Exception(prediction["request_log"]["message"])

        # if rid parameter exists, the user clicked the "explore" link of a 
        # ranking result, so register this as feedback to the previous request
        request_object = None

        if previous_request:
            request_object = MLRequest.objects.get(id=previous_request)
            previous_ranking = ast.literal_eval(request_object.ranking)
            # find this topic in the previous request ranking
            previous_input = ast.literal_eval(request_object.input_data)
            prediction["request_log"]["feedback_to"] = previous_input["q"]
            # get the similarity score for the previous topic
            score = dict(previous_ranking)[lookup.id]
            # save this topic and its score as feedback
            prediction["request_log"]["similarity"] = score
            prediction["request_log"]["rank"] = previous_request_rank
            if (request_object.feedback is not None 
                and request_object.feedback != ""):
                # append this query as new feedback to the previous feedback
                old_feedback = ast.literal_eval(request_object.feedback)
                new_feedback = {
                    'topic':lookup.name,
                    'similarity':score,
                    'rank': previous_request_rank
                }
                old_feedback.append(new_feedback)
                request_object.feedback = str(old_feedback)
            else:
                request_object.feedback = str([{
                    'topic':lookup.name,
                    'similarity':score,
                    'rank': previous_request_rank
                }])
            request_object.save()

            params["rid"] = previous_request
            params["i"] = previous_request_rank

        # Log the request-response in a MLRequest object
        ml_request = MLRequest(
            input_data=str(params),
            response=prediction["request_log"]["status"],
            full_response=prediction["request_log"],
            ranking=prediction["ranked_ids"],
            feedback="",
            parent_mlalgorithm=db_algorithms[algo_index],
            user_session=user_session,
            previous_request=request_object
        )
        ml_request.save()

        self.request_id = ml_request.id

        if featured:
            ranking = prediction["ranking"]["featured"] #Topic.objects.filter(id__in=top_pks, featured=True)
        else:
            ranking = prediction["ranking"]["all"] #Topic.objects.filter(id__in=top_pks)

        return ranking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, "request_id"):
            context["request_id"] = self.request_id
        context["timestamp"] = timezone.now()
        context["topic_names"] = list(
            Topic.objects.values_list('display_name', flat=True)
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        context["total_time"] = (timezone.now() - self._start_time).total_seconds()
        # self.request.session["context"] = context
        return super().render_to_response(context, **response_kwargs)