from django.urls import path
from .views import (
    EventListCreateView,
    EventDetailView,
    EnrollEventView,
    MyEventsView,
    UpcomingEnrollmentsView,
    PastEnrollmentsView
)

urlpatterns = [
    path(
        '',
        EventListCreateView.as_view(),
        name='event-list-create'
    ),
    path(
    'enrollments/past/',
    PastEnrollmentsView.as_view(),
    name='past-enrollments'
),
    path(
    'enrollments/upcoming/',
    UpcomingEnrollmentsView.as_view(),
    name='upcoming-enrollments'
),
    path(
    'my-events/',
    MyEventsView.as_view(),
    name='my-events'
),
    path(
    '<int:pk>/',
    EventDetailView.as_view(),
    name='event-detail'
    ),
    path(
    '<int:pk>/enroll/',
    EnrollEventView.as_view(),
    name='event-enroll'
    ),
]