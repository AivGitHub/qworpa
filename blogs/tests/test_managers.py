from django.test import TestCase

from blogs.managers import PostManager


class PostManagerTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_normalized_weights_returns_weights_with_sum_equals_to_1_when_initial_sum_equals_to_2(self):
        initial_weights = [
            {'weight': 0.9},
            {'weight': 0.9},
            {'weight': 0.2},
        ]
        self.assertEqual(sum(_i['weight'] for _i in initial_weights), 2, 'Sum of weights must be 2')
        normalized_weights = PostManager.get_normalized_weights(initial_weights)
        self.assertEqual(normalized_weights.sum(), 1, 'Sum of normalised weights must be 1')
