from notification.utils import get_comment_action
from products.models import Comment


# navbar에 사용될 notification
def get_actions(request):
    action_qs = get_comment_action(request, comment=Comment)
    return dict(action_qs=action_qs)
