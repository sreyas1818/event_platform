from rest_framework.permissions import BasePermission


class IsFacilitator(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and
            request.user.userprofile.role == "FACILITATOR"
        )


class IsSeeker(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and
            request.user.userprofile.role == "SEEKER"
        )