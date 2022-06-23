from ast import literal_eval as eval
from statistics import fmean

from django.utils import timezone

from ml_api.models import *
from ml_algorithms.cosine_ranking import CosineSimilarityRecommender
from ml_algorithms.random_ranking import RandomRecommender

class MLRegistry:
    _instance = None # singleton

    ENDPOINT_TOPICS = "topics_recommender"

    STATUS_AB_TESTING = "ab_testing"
    STATUS_PREPRODUCTION = "preproduction"

    _endpoints_ = (ENDPOINT_TOPICS,)
    _endpoint_statuses_ = (STATUS_AB_TESTING, STATUS_PREPRODUCTION,)
    _endpoint_algorithms = {}
    
    def __init__(self):
        # this logic has been moved inside __new__
        pass

    def __new__(cls):
        self = cls._instance
        if self is None:
            self = super(MLRegistry, cls).__new__(cls)
            # make sure all the endpoints are in the database
            for ep in self._endpoints_:
                Endpoint.objects.get_or_create(name=ep)

            # create and register objects for each algorithm in the database
            for algorithm in MLAlgorithm.objects.all():
                if algorithm.parent_endpoint.name != self.ENDPOINT_TOPICS:
                    raise Exception(f"Unknown endpoint for algorithm {algorithm.id}: {algorithm.parent_endpoint.name}")
                if algorithm.name == CosineSimilarityRecommender.ALGORITHM_COSINE:
                    algo_object = CosineSimilarityRecommender(algorithm.name)
                elif algorithm.name == RandomRecommender.ALGORITHM_RANDOM:
                    algo_object = RandomRecommender(algorithm.name)
                else:
                    raise Exception(f"Unknown algorithm {algorithm.id}: {algorithm.name}")
                self.register_algorithm(algorithm.id, algo_object)
                cls._instance = self
        return self

    def add_algorithm(self, endpoint_name, algorithm_object, algorithm_name, 
                      algorithm_version, algorithm_description, active):
        """Ensures that a given algorithm is loaded in the registry and has an associated database object.
        The algorithm will be created in the database if it does not already exist.

        Args:
            endpoint_name (str): The API endpoint associated with this algorithm.
            algorithm_object (ml_algorithms.topics.TopicsRecommender): An instance of the recommender object.
            algorithm_name (str): The name of the algorithm used for this recommender.
            algorithm_status (str): The status of the algorithm in the system.
            algorithm_version (str): A numerical notation of the algorithm version.
            algorithm_description (str): A short description of the algorithm model.

        Returns:
            int: The ID of the algorithm's corresponding database object.
        """
        # get endpoint record from the database
        endpoint = Endpoint.objects.get(name=endpoint_name)

        # create algorithm record in the database or get existing one
        db_object, created = MLAlgorithm.objects.get_or_create(
            name=algorithm_name,
            description=algorithm_description,
            version=algorithm_version,
            parent_endpoint=endpoint,
            active=active
        )

        # only allow multiple active algorithms if this endpoint status is "ab_testing"
        active_algorithms = MLAlgorithm.objects.filter(
            parent_endpoint=endpoint,
            active=True
        )
        if (len(active_algorithms)) > 1:
            ep_status = endpoint.status.get(active=True)
            if (ep_status.status != self.STATUS_AB_TESTING):
                if created and active:
                    db_object.delete()
                    raise Exception(f"CONFIGURATION ERROR: Unable to add a new algorithm to endpoint {endpoint_name}")
                else:
                    raise Exception(f"CONFIGURATION ERROR: Multiple active algorithms for endpoint {endpoint_name}")

        # register the DB object and return its ID
        self.register_algorithm(db_object.id, algorithm_object)
        return db_object.id

    def register_algorithm(self, db_id, algorithm_object):
        """
        Add to the algorithm object to the registry dictionary and 
        associate it with its corresponding DB object ID.
        """
        if not MLAlgorithm.objects.filter(id=db_id).exists():
            raise Exception(f"Algorithm (id={db_id}) is not registered in the database.")
        self._endpoint_algorithms[db_id] = algorithm_object

    def is_registered(self, endpoint_name, algorithm_name, 
                      algorithm_version):
        db_objects = MLAlgorithm.objects.filter(
            parent_endpoint__name=endpoint_name,
            name=algorithm_name,
            version=algorithm_version
        )
        return (
                len(db_objects) > 0 and
                db_objects[0].id in self._endpoint_algorithms.keys()
        )

    def get_algorithm(self, db_object_id):
        if db_object_id in self._endpoint_algorithms.keys():
            return self._endpoint_algorithms[db_object_id]
        else:
            return None
    
    # def update_algorithm_status(self, db_id, algorithm_object, algorithm_status):
    #     #TODO: Manage algorithm, endpoint, and status relationships
    #     pass

    def deactivate_other_statuses(self, status):
        """Deactivate all other statuses sharing an endpoint with the given status."""
        old_statuses = MLTestingStatus.objects.filter(
            parent_endpoint=status.parent_endpoint,
            created_at__lt=status.created_at,
            active=True
        )
        for other_status in old_statuses:
            if other_status.created_at > status.created_at:
                raise Exception(f"CONFIGURATION ERROR: Attempting to deactive newer existing status {other_status}")
            other_status.active = False
        MLTestingStatus.objects.bulk_update(old_statuses, ["active"])

    def register_ab_testing(self, endpoint_name):
        """Changes the given endpoint status to ab_testing"""
        endpoint = Endpoint.objects.get(name=endpoint_name)

        # check if A/B testing status is already active
        ab_status, _ = MLTestingStatus.objects.get_or_create(
            status=self.STATUS_AB_TESTING,
            active=True,
            parent_endpoint=endpoint
        )
        self.deactivate_other_statuses(ab_status)

        # make a new active ABTest record if it doesn't exist


    def begin_ab_testing(self, endpoint_name):
        """Creates a new A/B Test and associates it with the endpoint."""
        ab_test, created = ABTest.objects.get_or_create(
            title=endpoint_name,
            ended_at=None
        )
        if not created:
            print(" ### WARNING ###", " A/B Test is already running.")
        #     ab_test.created_at = timezone.now()
        #     ab_test.save()
            
        endpoint = Endpoint.objects.get(name=endpoint_name)
        endpoint.ab_test = ab_test
        endpoint.save()

    def end_ab_testing(self, endpoint_name):
        """Collects and summarizes all the requests on the given endpoint over the
        duration of the active A/B Test. Requests are organized by user session 
        within each respective algorithm. The summary also produces mean similarity 
        scores and rankings for requests that are feedback on previous searches. The
        mean scores are aggregated for all requests in the user session as well as
        for all requests of each algorithm.

        Args:
            endpoint_name (str): The name of the Endpoint object in the database

        Raises:
            Exception: The endpoint does not have an active A/B Test.
        """
        endpoint = Endpoint.objects.get(name=endpoint_name)
        if endpoint.ab_test is None or endpoint.ab_test.ended_at is not None:
            raise Exception(f"Unable to find active A/B Test for endpoint {endpoint_name}.")

        summary = {}
        for algo in endpoint.algorithms.all():
            # get all related requests during the A/B Test active time
            ml_requests = MLRequest.objects.filter(
                parent_mlalgorithm=algo,
                created_at__gt=endpoint.ab_test.created_at
            )
            # get all user sessions from the requests
            usessions = (ml_requests.all()
                         .values_list("user_session", flat=True)
                         .distinct())
            algo_summary = {
                "algo_mean_score": 0,
                "algo_mean_rank": 0,
                "sessions": {}
            }
            # all similarity scores and ranks for topics chosen with this algorithm
            algo_scores = []
            algo_ranks = []

            for usession in usessions:
                user_requests = ml_requests.filter(user_session=usession)
                session_scores = []
                session_ranks = []

                # create a flat list of requests, accounting for branching paths
                while user_requests: # trace a linked history of searches
                    # build on an existing history for this user session
                    trace = algo_summary["sessions"].get(usession.hex, {
                        "mean_score": 0,
                        "mean_rank": 0,
                        "requests": []
                    })
                    latest_request = user_requests.latest()
                    while latest_request: # until there are no more previous requests
                        user_requests = user_requests.exclude(pk=latest_request.pk)
                        # skip this request if it might be an error
                        if latest_request.response != "OK":
                            if len(user_requests) > 0:
                                latest_request = user_requests.latest()
                            else:
                                latest_request = None
                            continue
                        full_response = eval(latest_request.full_response)
                        r = {"topic": full_response["topic"],"id": full_response["id"]}
                        if "feedback_to" in full_response.keys():
                            r["feedback_to"] = full_response["feedback_to"]
                            r["similarity"] = full_response["similarity"]
                            r["rank"] = full_response["rank"]
                            if r not in trace["requests"]:
                                session_scores.append(float(r["similarity"]))
                                session_ranks.append(int(r["rank"]))
                        # add/move the request to the front of the trace
                        if r in trace["requests"]:
                            trace["requests"].remove(r)
                        trace["requests"].insert(0,r)
                        
                        # iterate while there are linked requests
                        latest_request = latest_request.previous_request
                    
                    # save this trace to the user session
                    algo_summary["sessions"][usession.hex] = trace

                # summarize session after all requests for this user have been added
                if len(session_scores) > 0:
                    algo_summary["sessions"][usession.hex]["mean_score"] = fmean(session_scores)
                    algo_summary["sessions"][usession.hex]["mean_rank"] = fmean(session_ranks)

                algo_scores += session_scores
                algo_ranks += session_ranks

            if len(algo_scores) > 0:
                algo_summary["algo_mean_score"] = fmean(algo_scores)
                algo_summary["algo_mean_rank"] = fmean(algo_ranks)

            summary[algo.name] = algo_summary
            
        endpoint.ab_test.summary = str(summary)
        endpoint.ab_test.ended_at = timezone.now()

        endpoint.ab_test.save()

        #TODO: deactivate the endpoint testing status 
                    
        #TODO: calculate a summary and close the active A/B Test
        #   ( values_list('user_session', flat=True).distinct() )
        #   for each user session
        #     while there are still requests for this user session
        #       filter most recent MLRequest
        #       stack requests linked through each previous request field
        #         remove requests from set as they are stacked
        #       save request stack
        #     average the feedback similarity scores and ranks
        #     save average scores, rank, and request stacks
        #     

    def __str__(self):
        return str(self._endpoint_algorithms)

    def __len__(self):
        return len(self._endpoint_algorithms)

