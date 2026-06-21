from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, CarReview

def blog_home(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    return render(request, 'blog_module/home.html', {'posts': posts_page})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views += 1
    post.save()
    return render(request, 'blog_module/detail.html', {'post': post})

def car_reviews(request):
    reviews = CarReview.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'blog_module/car_reviews.html', {'reviews': reviews})