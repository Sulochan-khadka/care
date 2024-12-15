from django.db import transaction
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend

from care.emr.api.viewsets.base import EMRModelViewSet
from care.emr.models.scheduling.schedule import Schedule
from care.emr.resources.scheduling.schedule.spec import (
    ScheduleReadSpec,
    ScheduleWriteSpec,
)
from care.users.models import User


class ScheduleFilters(FilterSet):
    pass


class ScheduleViewSet(EMRModelViewSet):
    database_model = Schedule
    pydantic_model = ScheduleWriteSpec
    pydantic_read_model = ScheduleReadSpec
    filterset_class = ScheduleFilters
    filter_backends = [DjangoFilterBackend]
    CREATE_QUESTIONNAIRE_RESPONSE = False

    def perform_create(self, instance):
        with transaction.atomic():
            super().perform_create(instance)
            for availability in instance.availabilities:
                availability_obj = availability.de_serialize()
                availability_obj.schedule = instance
                availability_obj.save()

    def clean_create_data(self, request_data):
        request_data["facility"] = self.kwargs["facility_external_id"]
        return request_data

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(resource__facility__external_id=self.kwargs["facility_external_id"])
            .select_related("resource", "created_by", "updated_by")
            .order_by("-modified_date")
        )
        if (
            self.request.GET.get("resource")
            and self.request.GET.get("resource_type")
            and self.request.GET.get("resource_type") == "user"
        ):
            user_obj = User.objects.filter(
                external_id=self.request.GET.get("resource")
            ).first()
            if user_obj:
                queryset = queryset.filter(resource__resource_id=user_obj.id)
        return queryset
