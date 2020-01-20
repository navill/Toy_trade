from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from products.forms import ProductForm, CommentForm
from products.models import Product, Comment


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.save(commit=False)
            data.user = request.user
            data.save()
            return redirect(data.get_absolute_url())


class ProductListView(ListView):
    queryset = Product.objects.all().owner()
    template_name = 'products/product_list.html'
    paginate_by = 3


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'products/product_detail.html'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        comments = Comment.objects.prefetch_related('product').filter(product=obj)
        # 템플릿에 전달되어야 하는 값: product_obj, comments,
        context = {
            'object': obj,
            'comments': comments,
        }
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
            product = Product.objects.get(id=form.data['product'])
            data.product = product
            data.save()
            return redirect(product.get_absolute_url())
