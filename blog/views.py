from django.shortcuts import render, get_object_or_404
from .models import BlogPost, CarReview

def blog_home(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'blog/home.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views += 1
    post.save()
    return render(request, 'blog/detail.html', {'post': post})

def car_reviews(request):
    reviews = CarReview.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'blog/car_reviews.html', {'reviews': reviews})