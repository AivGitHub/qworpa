from django.db.models import Manager


class PostManager(Manager):
    use_in_migrations = True
