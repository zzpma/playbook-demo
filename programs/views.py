# programs/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
import stripe

from .forms import ProgramForm
from .models import Program, Registration
from payments.models import Payment

@login_required
def create_program(request):
    if request.method == "GET":
        return render(
            request,
            "programs/create_program.html",
            {"form": ProgramForm()}
        )

    # --- POST ---
    form = ProgramForm(request.POST)

    if not form.is_valid():
        return render(
            request,
            "programs/create_program.html",
            {"form": form}
        )

    program = form.save(commit=False)
    program.created_by = request.user
    program.save()

    # Create Stripe Product + Price
    try:
        product = stripe.Product.create(
            name=program.name,
            description=program.description,
            metadata={"program_id": program.id}
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(float(program.price) * 100),
            currency="usd"
        )

        # Save Stripe IDs if present
        if hasattr(program, "stripe_product_id"):
            program.stripe_product_id = product.id
        if hasattr(program, "stripe_price_id"):
            program.stripe_price_id = price.id

        program.save()

    except Exception as e:
        print("Stripe creation error:", e)
        messages.warning(
            request,
            "Program created, but Stripe product could not be created."
        )

    messages.success(request, "Program created successfully!")
    return redirect("temp_dashboard")


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
