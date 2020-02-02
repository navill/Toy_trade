import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import Action


# action 생성
def create_action(user, verb, obj=None, target_user=None):
    now = timezone.now()
    # 반복 동작은 1분으로 제한
    last_minute = now - datetime.timedelta(seconds=60)
    # 객체가 생성된 시간보다 현재(create_action이 실행된 시점 + 60초) 보다 큰 객체를 filtering -> 반복적인 동작을 막기 위함
    similar_actions = Action.objects.filter(user_id=user.id, verb=verb, created__gte=last_minute)
    if obj:
        content_type = ContentType.objects.get_for_model(obj)
        similar_actions = similar_actions.filter(content_type=content_type, object_id=obj.id)
    if not similar_actions:
        action = Action(user=user, target_user=target_user, verb=verb, content_object=obj)
        action.save()
        return True
    return False


def get_comment_action(request, comment=None):
    user = request.user
    comment_actions = None
    if user.is_authenticated:
        action_qs = Action.objects.filter(check=False)
        # 내가 쓴 글(product) + 내가 쓴 댓글(comment)은 제외
        comments = None
        try:
            comments = comment.objects.exclude(user=user).filter(product__user=user)

        except:
            pass
        if user.userprofile.filtered_city:
            comments = comments.filter(city=user.userprofile.city)
        ids = [c.id for c in comments]
        # 앞에서 필터링된 모든 Comment의 Action
        comment_actions = action_qs.prefetch_related('content_object').by_model(comment)
        comment_actions = comment_actions.filter(object_id__in=ids).order_by('-created')

    return comment_actions
