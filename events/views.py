from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Event
from .models import Enrollment
from .serializers import EventSerializer
from django.shortcuts import get_object_or_404
from accounts.permissions import IsFacilitator
from django.utils import timezone
from django.db.models import Q
from .pagination import EventPagination
from django.core.mail import send_mail

class EventListCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        events = Event.objects.all()

        location = request.query_params.get(
            'location'
        )

        language = request.query_params.get(
            'language'
        )

        starts_after = request.query_params.get(
            'starts_after'
        )

        starts_before = request.query_params.get(
            'starts_before'
        )

        search = request.query_params.get(
            'q'
        )

        ordering = request.query_params.get(
            'ordering'
        )

        if location:

            events = events.filter(
                location__icontains=location
            )

        if language:

            events = events.filter(
                language__icontains=language
            )

        if starts_after:

            events = events.filter(
                starts_at__gte=starts_after
            )

        if starts_before:

            events = events.filter(
                starts_at__lte=starts_before
            )

        if search:

            events = events.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if ordering:

            events = events.order_by(
                ordering
            )

        paginator = EventPagination()

        page = paginator.paginate_queryset(
         events,
            request
        )

        serializer = EventSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):

        if request.user.userprofile.role != "FACILITATOR":

            return Response(
                {
                    "detail":
                    "You do not have permission to perform this action.",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EventSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        event = serializer.save(
            created_by=request.user
        )

        return Response(
            EventSerializer(event).data,
            status=status.HTTP_201_CREATED
        )
class EventDetailView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, pk):

        event = get_object_or_404(
            Event,
            pk=pk
        )

        serializer = EventSerializer(
            event
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        event = get_object_or_404(
            Event,
            pk=pk
        )

        # Only facilitators can update
        if request.user.userprofile.role != "FACILITATOR":

            return Response(
                {
                    "detail":
                    "Only facilitators can update events",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Only creator can update
        if event.created_by != request.user:

            return Response(
                {
                    "detail":
                    "You can only update your own events",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EventSerializer(
            event,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):

        event = get_object_or_404(
            Event,
            pk=pk
        )

        # Only facilitators can delete
        if request.user.userprofile.role != "FACILITATOR":

            return Response(
                {
                    "detail":
                    "Only facilitators can delete events",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Only creator can delete
        if event.created_by != request.user:

            return Response(
                {
                    "detail":
                    "You can only delete your own events",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        event.delete()

        return Response(
            {
                "message":
                "Event deleted successfully"
            },
            status=status.HTTP_200_OK
        )
        
class EnrollEventView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        event = get_object_or_404(
            Event,
            pk=pk
        )

        if request.user.userprofile.role != "SEEKER":

            return Response(
                {
                    "detail":
                    "Only seekers can enroll",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        already_enrolled = Enrollment.objects.filter(
            event=event,
            seeker=request.user,
            status='ENROLLED'
        ).exists()

        if already_enrolled:

            return Response(
                {
                    "detail":
                    "Already enrolled",
                    "code":
                    "already_enrolled"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        enrolled_count = Enrollment.objects.filter(
            event=event,
            status='ENROLLED'
        ).count()

        if (
            event.capacity is not None and
            enrolled_count >= event.capacity
        ):

            return Response(
                {
                    "detail":
                    "Event is full",
                    "code":
                    "event_full"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment = Enrollment.objects.filter(
            event=event,
            seeker=request.user
        ).first()

        if enrollment:

            if enrollment.status == 'ENROLLED':

                return Response(
                    {
                    "detail": "Already enrolled",
                    "code": "already_enrolled"
                    },
                status=status.HTTP_400_BAD_REQUEST
                )

            enrollment.status = 'ENROLLED'
            enrollment.save()

        else:

            Enrollment.objects.create(
            event=event,
            seeker=request.user,
            status='ENROLLED'
        )
        send_mail(
            subject=f'Enrollment Confirmed - {event.title}',
            message=(
                f'Hello {request.user.username},\n\n'
                f'You have successfully enrolled in:\n\n'
                f'Event: {event.title}\n'
                f'Location: {event.location}\n'
                f'Starts: {event.starts_at}\n'
                f'Ends: {event.ends_at}\n\n'
                f'Thank you.'
            ),
            from_email='sreyas593@gmail.com',
            recipient_list=[request.user.email],
            fail_silently=False
        )

        return Response(
            {
                "message":
                "Enrollment successful"
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):

        event = get_object_or_404(
            Event,
            pk=pk
        )

        if request.user.userprofile.role != "SEEKER":

            return Response(
                {
                    "detail":
                    "Only seekers can cancel enrollments",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        enrollment = Enrollment.objects.filter(
            event=event,
            seeker=request.user,
            status='ENROLLED'
        ).first()

        if not enrollment:

            return Response(
                {
                    "detail":
                    "Enrollment not found",
                    "code":
                    "enrollment_not_found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        enrollment.status = 'CANCELLED'

        enrollment.save()

        return Response(
            {
                "message":
                "Enrollment cancelled successfully"
            },
            status=status.HTTP_200_OK
        )

class MyEventsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        if request.user.userprofile.role != "FACILITATOR":

            return Response(
                {
                    "detail":
                    "Only facilitators can view this resource",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        events = Event.objects.filter(
            created_by=request.user
        )

        response_data = []

        for event in events:

            enrolled_count = Enrollment.objects.filter(
                event=event,
                status='ENROLLED'
            ).count()

            response_data.append({
                "id": event.id,
                "title": event.title,
                "capacity": event.capacity,
                "total_enrollments": enrolled_count,
                "available_seats":
                    event.capacity - enrolled_count
                    if event.capacity is not None
                    else None
            })

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )
class UpcomingEnrollmentsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        if request.user.userprofile.role != "SEEKER":

            return Response(
                {
                    "detail":
                    "Only seekers can view enrollments",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        enrollments = Enrollment.objects.filter(
            seeker=request.user,
            status='ENROLLED',
            event__ends_at__gt=timezone.now()
        )

        data = []

        for enrollment in enrollments:

            event = enrollment.event

            data.append({
                "id": event.id,
                "title": event.title,
                "location": event.location,
                "starts_at": event.starts_at,
                "ends_at": event.ends_at
            })

        return Response(
            data,
            status=status.HTTP_200_OK
        )

class PastEnrollmentsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        if request.user.userprofile.role != "SEEKER":

            return Response(
                {
                    "detail":
                    "Only seekers can view enrollments",
                    "code":
                    "permission_denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        enrollments = Enrollment.objects.filter(
            seeker=request.user,
            status='ENROLLED',
            event__ends_at__lt=timezone.now()
        )

        data = []

        for enrollment in enrollments:

            event = enrollment.event

            data.append({
                "id": event.id,
                "title": event.title,
                "location": event.location,
                "starts_at": event.starts_at,
                "ends_at": event.ends_at
            })

        return Response(
            data,
            status=status.HTTP_200_OK
        )