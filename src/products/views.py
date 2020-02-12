from django.http import Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from location.naver_geolocation import google_distance_matrix
from products.forms import ProductForm, CommentForm
from products.models import Product, Comment


def set_object_location(request, data, save=False):
    session = request.session
    data.user = request.user
    data.city = session['city']
    data.lat = session['geo_address']['lat']
    data.lng = session['geo_address']['long']
    # comment & product object에 현재 위치의 좌표 저장
    if save:
        data.save()


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.save(commit=False)
            set_object_location(request, data, save=True)
            return redirect(data.get_absolute_url())


class ProductListView(ListView):
    queryset = Product.objects.all().with_user().with_comment()
    template_name = 'products/product_list.html'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        city = kwargs.get('city')
        q = request.GET.get('q')
        qs = self.get_queryset()
        # 동(논현, 서초 등..)별로 필터
        if city:
            qs = qs.filter(city=city)
        # search에 입력된 값을 이용한 필터
        if q:
            qs = qs.filter(title__icontains=q)

        context = self.get_context_data(object_list=qs)
        context['city'] = city
        return render(request, 'products/product_list.html', context=context)


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
        # 템플릿에 전달되어야 하는 값: product_obj, comments
        context_data = {
            'object': obj,
            'comments': comments,
        }
        return render(request, 'products/product_detail.html', context=context_data)


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
        # form = self.get_form()
        form = CommentForm(data=request.POST)
        pk = kwargs.get('pk', None)
        if form.is_valid():
            product = Product.objects.get(id=pk)
            data = form.save(commit=False)
            # comment obj에 위치 정보 저장
            set_object_location(request, data)
            p_latlng = str(product.lat) + ',' + str(product.lng)
            c_latlng = str(data.lat) + ',' + str(data.lng)
            data.product = product
            # product-comment의 거리 측정
            distance = google_distance_matrix(org_coord=p_latlng, des_coord=c_latlng)
            print('distance', distance)
            data.distance = distance[c_latlng]['distance']['text']
            print(data.distance)
            data.save()
            return redirect(product.get_absolute_url())


class CommentDeleteView(DeleteView):
    model = Comment
    success_url = ''

    def get_object(self, queryset=None):
        obj = super(CommentDeleteView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        comment = obj.product
        obj.delete()
        return redirect(comment.get_absolute_url())
