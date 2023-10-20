
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


from .. import models


def make_user_follow_or_unfollow_user(follower: 'models.User', followed: 'models.User', should_follow: bool):
    if should_follow:
        # attempt to create a following record
        _, _ = models.UserFollowingUser.objects.get_or_create(
            follower=follower,
            followed=followed
        )
    else:
        # attempt to delete following record
        try:
            models.UserFollowingUser.objects.filter(
                follower=follower,
                followed=followed
            ).get().delete()
        except models.UserFollowingUser.DoesNotExist:
            pass
