from django.db.models import Case, Manager, When
from numpy import array, random


class PostManager(Manager):
    use_in_migrations = True

    @staticmethod
    def get_normalized_weights(posts_data):
        """Returns normalized weights.

        Populates weights in case weight equals to 0.

        posts_data (django.db.models.query.QuerySet): which contains ``weight``.

        Returns:
            numpy.ndarray: Normalized weights. Important is that sum of weights must be 1, it's required by numpy.
        """
        # TODO: Should be removed when there are no records with weights = 0.
        weights = array(
            [post_data['weight'] if post_data['weight'] else random.uniform(low=0.01, high=0.5)
             for post_data
             in posts_data]
        )
        return weights / weights.sum()

    def smart_select(self, max_quantity=5):
        """Selects posts according to their weights.

        max_quantity (int): Maximum allowed quantity of posts.
        """
        posts = self.exclude(is_draft=True).order_by('id').values('id', 'weight')[:1000]
        total_posts = posts.count()
        quantity = min(max_quantity, total_posts)
        if quantity == 0:
            return []
        if total_posts == 1:
            return self.filter(id=posts[0]['id'])

        ids = random.choice(
            [post_data['id'] for post_data in posts],
            size=max_quantity,
            replace=False,
            p=PostManager.get_normalized_weights(posts)
        )
        return self.filter(id__in=ids).order_by(Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)]))
