"""
WSGI config for Topics_RS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""
###############################
####### Django Defaults #######
###############################

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Topics_RS.settings')
application = get_wsgi_application()

from topics_recommender.models import Topic

################################
##### Loading Topics Data ######
################################
if len(Topic.objects.all()) == 0:
    print("!!--- NO TOPICS IN THE DATABASE ---!!")
    print("  >> Run the load_csv command to populate topics.")

################################
#### ML Algorithms Registry ####
################################
from ml_algorithms.registry import MLRegistry
from ml_algorithms.cosine_ranking import CosineSimilarityRecommender
from ml_algorithms.random_ranking import RandomRecommender

registry = MLRegistry()

# activate A/B Testings status on the topics_recommender endpoint
registry.register_ab_testing(MLRegistry.ENDPOINT_TOPICS)

algos_to_add = (
    {
        "endpoint": MLRegistry.ENDPOINT_TOPICS,
        "name": CosineSimilarityRecommender.ALGORITHM_TFIDF,
        "version": "0.1",
        "description": "A ranking recommender algorithm based on cosine similarity scores.",
        "active": True,
    },
    {
        "endpoint": MLRegistry.ENDPOINT_TOPICS,
        "name": RandomRecommender.ALGORITHM_RANDOM,
        "version": "0.1",
        "description": "A baseline algorithm that randomly ranks topics but records their similarity scores.",
        "active": True,
    }
)

# add multiple algorithms to the topics_recommender endpoint for A/B testing
algo_cos = algos_to_add[0]
algorithm_obj_cos = CosineSimilarityRecommender(algo_cos["name"])
registry.add_algorithm(
    algo_cos["endpoint"],
    algorithm_obj_cos,
    algo_cos["name"],
    algo_cos["version"],
    algo_cos["description"],
    algo_cos["active"]
)

algo_rand = algos_to_add[1]
algorithm_obj_rand = RandomRecommender(algo_rand["name"])
registry.add_algorithm(
    algo_rand["endpoint"],
    algorithm_obj_rand,
    algo_rand["name"],
    algo_rand["version"],
    algo_rand["description"],
    algo_rand["active"]
)

# initialize the A/B Test to include the newly added algorithms
registry.begin_ab_testing(registry.ENDPOINT_TOPICS)