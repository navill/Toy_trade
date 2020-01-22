import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import Action


# action 생성
def create_action(user, verb, obj=None):
    now = timezone.now()
    # 반복 동작은 1분으로 제한
    last_minute = now - datetime.timedelta(seconds=60)
    # 객체가 생성된 시간보다 현재(create_action이 실행된 시점 + 60초) 보다 큰 객체를 filtering -> 반복적인 동작을 막기 위함
    similar_actions = Action.objects.filter(user_id=user.id, verb=verb, created__gte=last_minute)
    if obj:
        content_type = ContentType.objects.get_for_model(obj)
        similar_actions = similar_actions.filter(content_type=content_type, object_id=obj.id)
    if not similar_actions:
        action = Action(user=user, verb=verb, content_object=obj)
        action.save()
        return True
    return False

