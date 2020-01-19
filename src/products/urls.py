from django.urls import path

from products.views import ProductListView, ProductDetailView, ProductCreateView, CommentCreateView, CommentListView

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('create/', ProductCreateView.as_view(), name='create'),
    path('<pk>/', ProductDetailView.as_view(), name='detail'),
    path('<pk>/comment/create/', CommentCreateView.as_view(), name='comment-create'),
    path('<pk>/comment/list/', CommentListView.as_view(), name='comment-list'),
]
