from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from products.models import Category, Product, Type


class ProductCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        categories = Category.objects.all()
        types = Type.objects.all()

        kwargs['categories'] = categories
        kwargs['types'] = types

        return super().get_context_data(**kwargs)


class ProductListView(LoginRequiredMixin, TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        categories = Category.objects.all()
        types = Type.objects.all()

        kwargs['categories'] = categories
        kwargs['types'] = types

        return super().get_context_data(**kwargs)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['sku', 'description', 'category', 'type', 'active']
    template_name = 'products/update.html'
    success_url = reverse_lazy('inventory_control:inventory-control-list')
    # success_message

    def get_context_data(self, **kwargs):
        categories = Category.objects.all()
        types = Type.objects.all()

        kwargs['categories'] = categories
        kwargs['types'] = types

        return super().get_context_data(**kwargs)