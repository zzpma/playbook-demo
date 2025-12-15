# programs/views.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
import stripe

from .forms import ProgramForm
from .models import Program, Registration
from payments.models import Payment


@login_required
def programs(request):
    programs = Program.objects.all().prefetch_related("sessions")

    return render(
        request,
        "programs/programs.html",
        {"programs": programs, "form": ProgramForm()}
    )


@login_required
def create_program(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    form = ProgramForm(request.POST)

    if not form.is_valid():
        # Re-render the form inside the dialog
        return render(
            request,
            "programs/partials/create_program_form.html",
            {"form": form},
            status=400
        )

    program = form.save(commit=False)
    program.created_by = request.user
    program.save()

    # --- Stripe (unchanged logic) ---
    try:
        product = stripe.Product.create(
            name=program.title,
            description=program.description,
            metadata={"program_id": program.id}
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(program.price * 100),
            currency="usd"
        )
        program.stripe_product_id = product.id
        program.stripe_price_id = price.id
        program.save()
    except Exception:
        messages.warning(request, "Program created, but Stripe setup failed.")

    # 🔥 HTMX response: return ONE table row
    return render(
        request,
        "programs/partials/program_row.html",
        {"program": program},
        status=201
    )


@login_required
@require_POST
def toggle_registration(request, program_id):
    program = get_object_or_404(Program, id=program_id)

    program.is_reg_open = not program.is_reg_open
    program.save(update_fields=["is_reg_open"])

    return render(
        request,
        "programs/partials/reg_toggle.html",
        {"program": program},
    )


@login_required
def public_register(request, public_id):
    program = get_object_or_404(Program, public_id=public_id)
    sessions = program.sessions.all()

    if request.method == "GET":
        return render(request, "programs/public_register.html", {
            "program": program,
            "sessions": sessions
        })

    # -----------------------------
    # 1. Extract & validate fields
    # -----------------------------
    participant_name = request.POST.get("participant_name", "").strip()
    email = request.POST.get("email", "").strip()
    quantity = int(request.POST.get("quantity", "1") or 1)

    if not participant_name or not email:
        messages.error(request, "Please provide participant name and email.")
        return render(request, "programs/public_register.html", {
            "program": program, 
            "sessions": sessions
        })

    # -----------------------------
    # 2. Create Registration
    # -----------------------------
    registration = Registration.objects.create(
        program=program,
        participant_name=participant_name,
        email=email,
        quantity=quantity
    )

    # -----------------------------
    # 3. Create Payment (PENDING)
    # -----------------------------
    amount_in_dollars = program.price * quantity

    payment_record = Payment.objects.create(
        registration_id=registration,
        amount=amount_in_dollars,
        status="PENDING"
    )

    # -----------------------------
    # 4. Create Stripe Checkout Session
    # -----------------------------
    try:
        checkout_session = stripe.checkout.Session.create(
            mode='payment',
            payment_method_types=['card'],
            line_items=[{
                "price": program.stripe_price_id,   # from Program auto-create
                "quantity": quantity
            }],
            client_reference_id=payment_record.id,
            success_url=request.build_absolute_uri(
                reverse("payment_success")
            ),
            cancel_url=request.build_absolute_uri(
                reverse("payment_cancel")
            ),
        )

        payment_record.stripe_id = checkout_session.id
        payment_record.save()

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        print("Stripe error:", e)
        messages.error(request, "Unable to create Stripe checkout.")
        return render(request, "programs/public_register.html", {
            "program": program, 
            "sessions": sessions
        })
