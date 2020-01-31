from django.db.models import Q

from notification.models import Action


def get_actions(request):
    user = request.user
    action_qs = Action.objects.prefetch_related('content_object').filter(check=False)
    if user.is_authenticated:
        action_qs = action_qs.filter(
            ~Q(user=user) & Q(target_user=user)  # comment
        )
    return dict(action_qs=action_qs)
