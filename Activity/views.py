# 3. VIEWS (views.py)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Activity, Category
from .forms import ActivityForm, CategoryForm, CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    activities = Activity.objects.filter(user=request.user)
    
    # Statistics
    total_activities = activities.count()
    completed_activities = activities.filter(status='completed').count()
    in_progress = activities.filter(status='in_progress').count()
    overdue = sum(1 for activity in activities if activity.is_overdue)
    
    # Recent activities
    recent_activities = activities[:5]
    
    # Category statistics
    category_stats = Category.objects.annotate(
        activity_count=Count('activities', filter=Q(activities__user=request.user))
    ).filter(activity_count__gt=0)
    
    context = {
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'in_progress': in_progress,
        'overdue': overdue,
        'recent_activities': recent_activities,
        'category_stats': category_stats,
    }
    return render(request, 'activities/dashboard.html', context)

@login_required
def activity_list(request):
    activities = Activity.objects.filter(user=request.user)
    
    # Filtering
    category_filter = request.GET.get('category') or ""
    status_filter = request.GET.get('status') or ""
    priority_filter = request.GET.get('priority') or ""
    search = request.GET.get('search') or ""

    if category_filter.isdigit():
        activities = activities.filter(category_id=category_filter)
    if status_filter:
        activities = activities.filter(status=status_filter)
    if priority_filter:
        activities = activities.filter(priority=priority_filter)
    if search:
        activities = activities.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(activities, 9)
    page = request.GET.get('page')
    activities = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    context = {
        'activities': activities,
        'categories': categories,
        'current_category': category_filter,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search,
    }
    return render(request, 'activities/activity_list.html', context)

@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    return render(request, 'activities/activity_detail.html', {'activity': activity})

@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            messages.success(request, 'Activity created successfully!')
            return redirect('activity_detail', pk=activity.pk)
    else:
        form = ActivityForm()
    return render(request, 'activities/activity_form.html', {'form': form, 'title': 'Create Activity'})

@login_required
def activity_update(request, pk):
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('activity_detail', pk=activity.pk)
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'activities/activity_form.html', {'form': form, 'title': 'Update Activity', 'activity': activity})

@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Activity deleted successfully!')
        return redirect('activity_list')
    return render(request, 'activities/activity_confirm_delete.html', {'activity': activity})

@login_required
def category_list(request):
    categories = Category.objects.annotate(
        activity_count=Count('activities', filter=Q(activities__user=request.user))
    )
    return render(request, 'activities/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'activities/category_form.html', {'form': form, 'title': 'Create Category'})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')