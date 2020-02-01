from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class ActionQuerySet(models.QuerySet):
    def by_model(self, model_class, model_queryset=False):
        # model_class - Product, Comment, UserProfile, (Order)
        c_type = ContentType.objects.get_for_model(model_class)
        qs = self.filter(content_type=c_type)

        if model_queryset:
            obj_ids = [x.object_id for x in qs]
            # 해당 모델에 대한 queryset 반환
            return model_class.objects.select_related('user').filter(pk__in=obj_ids)
        # Action에 대한 queryset 반환
        return qs


class ActionManager(models.Manager):
    def get_queryset(self):
        return ActionQuerySet(self.model, using=self._db)

    def all(self):
        return super(ActionManager, self).all()


class Action(models.Model):
    user = models.ForeignKey(User, related_name='actions', db_index=True, on_delete=models.CASCADE)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='target_user', null=True)
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # city = models.CharField(max_length=100, null=True, blank=True)
    check = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to={"model__in": ('product', 'comment', 'userprofile',)}, blank=True,
                                     null=True, related_name='target_obj',
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # GenericForeignKey에 대한 db는 생성하지 않는다.
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ActionManager()

    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        # 구현에 따라 조건문 필요 + query 정리
        # userprofile -> url: /<username>
        # product(14), comment(15) -> url: /detail/<id>
        # print(self.content_type)
        return self.content_object.get_absolute_url()
