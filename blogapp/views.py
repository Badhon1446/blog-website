from django.shortcuts import render, get_object_or_404,redirect
from .models import Post,Tag,Comment,Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,authenticate,logout
from .forms import PostForm, CommentForm, UpdateProfileForm,LoginForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    if request.method == 'POST':
        pass
    return render(request,'blogs/home.html')

def post_list(request):

    categoryQ = request.GET.get('category')
    tagQ = request.GET.get('tag')
    searchQ = request.GET.get('search')

    posts = Post.objects.all()

    if categoryQ:
        posts = posts.filter(category__name = categoryQ)
    if tagQ:
        posts = posts.filter(tag__name = tagQ)
    if searchQ:
        posts = posts.filter(
            Q(title__icontains = searchQ)
            |Q(content__icontains = searchQ)
            |Q(tag__name__icontains=searchQ)
            |Q(category__name__icontains=searchQ)
            
        ).distinct()

    paginator = Paginator(posts,2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'search_queary': searchQ,
        'category_queary': categoryQ,
        'tag_queary': tagQ
    }
    return render(request,'blogs/post_list.html',context)
    
def post_details(request,id):
    post = get_object_or_404(Post,id=id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)        
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_details',id = post.id)
    else:
        comment_form = CommentForm()
        
    comments = post.comment_set.all()
    is_liked = post.liked_users.filter(id=request.user.id).exists()
    like_count = post.liked_users.count()

    context  = {
            'post': post,
            'category': Category.objects.all(),
            'tag': Tag.objects.all(),
            'comments':comments,
            'comment_form':comment_form,
            'is_liked':is_liked,
            'like_count':like_count

    }
    post.view_count += 1
    post.save()
        
    return render(request,'blogs/post_details.html',context )

def like_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        if post.liked_users.filter(id=request.user.id).exists():
            post.liked_users.remove(request.user)
        else:
            post.liked_users.add(request.user)

    # redirect to post_details to reload page
    return redirect('post_details', id=post.id)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request,'blogs/post_create.html',{'form':form})
    
@login_required
def post_update(request, id):
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, instance=post)
    
    if form.is_valid():
        form.save()
        return redirect('post_details', id=post.id)
    
    context = {
        'form': form,
        'post': post  
    }
    return render(request, 'blogs/post_update.html', context)
@login_required
def post_delete(request,id):
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':

        post.delete()
        return redirect('post_list')
    return redirect('post_list')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request,'user/register.html',{'form':form})
@login_required
def profile(request):
    section = request.GET.get('section', 'profile')
    context = {'section' : section}

    if section == 'posts':
        posts = Post.objects.filter(author = request.user)
        context['posts']=posts
    elif section == 'update':
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('profile')
            
        else:
            form = UpdateProfileForm(instance=request.user)
        context['form'] = form
    return render(request,'user/profile.html',context)

def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")

    return render(request, 'user/login.html', {'form': form})
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')