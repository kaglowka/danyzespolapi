from celery import task
from mcod.counters.lib import Counter


@task()
def save_counters():
    counter = Counter()
    counter.save_counters()
    return {}
