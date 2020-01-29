import ast

from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from location.models import UserSession
from products.forms import ProductForm, CommentForm
from products.models import Product, Comment


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        user = request.user
        if form.is_valid():
            data = form.save(commit=False)
            data.user = user
            data.save()
            return redirect(data.get_absolute_url())


class ProductListView(ListView):
    queryset = Product.objects.all().with_user().with_comment()
    template_name = 'products/product_list.html'
    paginate_by = 3


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'products/product_detail.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        obj = Product.objects.filter(id=pk).with_user()  # Product(35) + user(1)
        return obj.first()

    def get(self, request, *args, **kwargs):
        # 필요한 모델 Product with User, Comment with User
        # 두 모델의 user 정보가 다르기 때문에 각각 select, prefetch 사용
        obj = self.get_object()
        comments = obj.comment_set.all().select_related('user__userprofile')  # comment(id:4,id:5) + user(id:1, id:2)
        # user_session = UserSession.objects.filter(user=request.user).first()
        # city = ast.literal_eval(user_session.city_data)
        # print(city['r3'])
        # 템플릿에 전달되어야 하는 값: product_obj, comments, city
        context = {
            'object': obj,
            'comments': comments,
            # 'city': city['r3']
        }
        # UserSession.objects.get(session_key=request.session.session_key)
        return render(request, 'products/product_detail.html', context=context)


class ProductUpdateView(UpdateView):
    queryset = Product.objects.all()


class ProductDeleteView(DeleteView):
    queryset = Product.objects.all()
    success_url = '/products/'


class CommentListView(ListView):
    queryset = Comment.objects.all()


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.save(commit=False)
            data.user = request.user
            # data.city = 'none'
            product = Product.objects.get(id=form.data['product'])
            data.product = product
            data.save()
            return redirect(product.get_absolute_url())
