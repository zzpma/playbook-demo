from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def dashboard(request):
    user = f"{request.user.first_name} {request.user.last_name[0]}."

    # Mock data to make the dashboard look "alive" immediately
    context = {
        'total_players': User.objects.count() + 80,
        'outstanding_fees': "$433",
        'upcoming_events': 3,
        'recent_activities': [
            {'action': 'New Registration', 'user': user, 'time': 'Just now'},
            {'action': 'Payment Received', 'user': 'Team Alpha', 'time': '5 hours ago'},
            {'action': 'Schedule Updated', 'user': 'Coach Mike', 'time': '1 day ago'},
        ]
    }
    return render(request, 'core/dashboard.html', context)
