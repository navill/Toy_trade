from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.

User = get_user_model()


class ActionQuerySet(models.QuerySet):
    def by_model(self, model_class, model_queryset=False):
        # model_class - Product, Comment, UserProfile, (Order)
        c_type = ContentType.objects.get_for_model(model_class)
        # 해당 content-type이 있는지 확인
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
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to={"model__in": ('product', 'comment', 'userprofile',)}, blank=True,
                                     null=True, related_name='target_obj',
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # GenericForeignKey에 대한 db는 생성하지 않는다.
    content_object = GenericForeignKey('content_type', 'object_id')
    check = models.BooleanField(default=False)
    
    objects = ActionManager()

    class Meta:
        ordering = ['-created']
