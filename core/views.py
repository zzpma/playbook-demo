from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from programs.models import Program

User = get_user_model()

@login_required
def dashboard(request):
    if request.user.last_name:
        user = f"{request.user.first_name} {request.user.last_name[0]}."
    else:
        user = request.user.first_name or request.user.username

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


@login_required
def temp_dashboard(request):
    """
    Temporary admin dashboard for Playbook demo.
    Shows live features and a dynamic list of programs (with absolute public links).
    """
    user = request.user
    display_name = user.get_full_name() or user.username

    # fetch programs created by this admin (adjust if you want all programs)
    qs = Program.objects.all().order_by("-id")[:50]

    # build absolute links for convenience so the demo flows work from anywhere
    program_links = []
    for p in qs:
        # Program.get_public_link returns a path like "/register/<uuid>/"
        # Use request.build_absolute_uri to make it a clickable full URL.
        try:
            full_link = request.build_absolute_uri(p.get_public_link())
        except Exception:
            # fallback in case get_public_link signature changed
            full_link = request.build_absolute_uri(f"/register/{p.public_id}/")
        program_links.append({
            "name": p.name,
            "link": full_link,
            "price": p.price,
            "deadline": p.registration_deadline,
        })

    context = {
        "display_name": display_name,
        "program_links": program_links,
    }
    return render(request, "core/temp_dashboard.html", context)
