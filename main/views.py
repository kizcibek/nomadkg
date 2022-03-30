from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView

from main.forms import *
from main.models import *
from main.permissions import UserHasPermissionMixin


class MainPageView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_template_names(self):
        template_name = super(MainPageView, self).get_template_names()
        search = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if search:
            template_name = 'search.html'
        elif filter:
            template_name = 'new.html'
        return template_name

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if search:
            context['products'] = Product.objects.filter(Q(title__icontains=search)|
                                                       Q(description__icontains=search))
        elif filter:
            start_date = timezone.now() - timedelta(days=1)
            context['products'] = Product.objects.filter(created__gte=start_date)
        else:
            context['products'] = Product.objects.all()

        return context




class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category-detail.html'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.slug = kwargs.get('slug', None)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(category_id=self.slug)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product-detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object().get_image
        context['images'] = self.get_object().images.exclude(id=image.id)
        return context


@login_required(login_url='login')
def add_product(request):    #CreateView -> model, template_name, context_object_name, form-class
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5)
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if product_form.is_valid() and formset.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.save()

            for form in formset.cleaned_data:
                image = form['image']
                Image.objects.create(image=image, product=product)
            return redirect(product.get_absolute_url())

    else:
        product_form = ProductForm()
        formset = ImageFormSet(queryset=Image.objects.none())
    return render(request, 'add-product.html', locals())


def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user == product.user:
        ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5)
        product_form = ProductForm(request.POST or None, instance=product)
        formset = ImageFormSet(request.POST or None, request.FILES or None, queryset=Image.objects.filter(procuct=product))
        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()

            for form in formset:
                image = form.save(commit=False)
                image.product = product
                image.save()
            return redirect(product.get_absolute_url())
        return render(request, 'update-product.html', locals())
    else:
        return HttpResponse('<h1>403 Forbidden</h1>')


class DeleteProductView(UserHasPermissionMixin, DeleteView):
    model = Product
    template_name = 'delete-product.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted!')
        return HttpResponseRedirect(success_url)
