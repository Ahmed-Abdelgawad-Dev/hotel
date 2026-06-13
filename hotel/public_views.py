from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from datetime import date
from decimal import Decimal

from hotel.rooms.models import RoomType
from hotel.inventory.services import AvailabilityService, PricingService, InventoryService
from hotel.inventory.models import MealPlan
from hotel.content.models import HeroSlide, Offer, GalleryImage, Review, NewsletterSubscriber


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["hero_slides"] = HeroSlide.objects.filter(is_active=True).order_by("sort_order")
        ctx["room_types"] = RoomType.objects.filter(is_active=True).order_by("sort_order")[:4]
        ctx["offers"] = Offer.objects.filter(is_active=True)[:3]
        ctx["reviews"] = Review.objects.filter(is_approved=True, is_featured=True)[:5]
        ctx["gallery_images"] = GalleryImage.objects.filter(is_active=True)[:6]
        return ctx


class RoomListView(ListView):
    model = RoomType
    template_name = "pages/rooms.html"
    context_object_name = "room_types"
    queryset = RoomType.objects.filter(is_active=True).order_by("sort_order")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["meal_plans"] = MealPlan.objects.filter(is_active=True)
        return ctx


class RoomDetailView(DetailView):
    model = RoomType
    template_name = "pages/room_detail.html"
    context_object_name = "room"
    slug_url_kwarg = "slug"


class GalleryView(TemplateView):
    template_name = "pages/gallery.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = GalleryImage.objects.filter(is_active=True).order_by("sort_order")
        ctx["gallery_categories"] = {
            "rooms": qs.filter(category="rooms"),
            "dining": qs.filter(category="dining"),
            "spa": qs.filter(category="spa"),
            "pool": qs.filter(category="pool"),
            "exterior": qs.filter(category="exterior"),
        }
        return ctx


class BookingSearchView(View):
    def get(self, request):
        try:
            check_in = date.fromisoformat(request.GET.get("check_in", ""))
            check_out = date.fromisoformat(request.GET.get("check_out", ""))
            adults = int(request.GET.get("adults", 1))
        except (ValueError, TypeError):
            return HttpResponse('<div class="text-red-500 p-4">Please provide valid dates.</div>')
        if check_in < date.today():
            return HttpResponse('<div class="text-red-500 p-4">Check-in must be in the future.</div>')
        if check_out <= check_in:
            return HttpResponse('<div class="text-red-500 p-4">Check-out must be after check-in.</div>')
        avail = AvailabilityService()
        pricing = PricingService()
        meal_plans = MealPlan.objects.filter(is_active=True)
        room_types = RoomType.objects.filter(is_active=True).order_by("sort_order")
        available = []
        for rt in room_types:
            if avail.check_range(rt.id, check_in, check_out):
                prices = {}
                for mp in meal_plans:
                    total = pricing.calculate(rt.id, mp.code, check_in, check_out)
                    if total:
                        prices[mp.code] = str(total)
                available.append({"room": rt, "prices": prices, "meal_plans": meal_plans})
        ctx = {
            "available": available, "check_in": check_in,
            "check_out": check_out, "adults": adults,
            "nights": (check_out - check_in).days,
        }
        return render(request, "public/partials/availability_results.html", ctx)


class NewsletterSubscribeView(View):
    def post(self, request):
        email = request.POST.get("email", "").strip()
        if not email or "@" not in email:
            return HttpResponse('<span class="text-red-500">Enter a valid email.</span>')
        _, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={"source": "footer_form", "ip_address": request.META.get("REMOTE_ADDR")},
        )
        if created:
            return HttpResponse('<span class="text-green-500">Subscribed!</span>')
        return HttpResponse('<span class="text-gold">Already subscribed!</span>')


class BookingSelectView(TemplateView):
    template_name = "pages/booking.html"

    def post(self, request, room_type_slug):
        try:
            room_type = RoomType.objects.get(slug=room_type_slug, is_active=True)
        except RoomType.DoesNotExist:
            return HttpResponse('<div class="text-red-500 p-4">Room not found.</div>', status=404)
        try:
            check_in = date.fromisoformat(request.POST.get("check_in", ""))
            check_out = date.fromisoformat(request.POST.get("check_out", ""))
            adults = int(request.POST.get("adults", 1))
            children = int(request.POST.get("children", 0))
        except (ValueError, TypeError):
            return HttpResponse('<div class="text-red-500 p-4">Invalid parameters.</div>', status=400)
        meal_plan_code = request.POST.get("meal_plan", "BB")
        try:
            meal_plan = MealPlan.objects.get(code=meal_plan_code, is_active=True)
        except MealPlan.DoesNotExist:
            meal_plan = MealPlan.objects.filter(is_active=True).first()
            if not meal_plan:
                return HttpResponse('<div class="text-red-500 p-4">No meal plans available.</div>', status=400)
        pricing = PricingService()
        total = pricing.calculate(room_type.id, meal_plan.code, check_in, check_out)
        breakdown = pricing.get_breakdown(room_type.id, meal_plan.code, check_in, check_out)
        if not total:
            return HttpResponse('<div class="text-red-500 p-4">No rate available.</div>', status=400)
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        inv = InventoryService()
        try:
            cart = inv.place_hold_and_create_cart(
                room_type=room_type, meal_plan=meal_plan,
                check_in=check_in, check_out=check_out,
                adults=adults, children=children,
                total_price=total, price_breakdown=breakdown,
                session_key=session_key,
            )
        except ValueError as e:
            return HttpResponse('<div class="text-red-500 p-4">{}</div>'.format(str(e)), status=409)
        request.session["cart_id"] = cart.id
        response = HttpResponse()
        response.headers["HX-Redirect"] = "/book/details/"
        return response
