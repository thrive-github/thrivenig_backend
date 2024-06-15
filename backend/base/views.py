from django.views.decorators.http import require_POST
from django.http import JsonResponse
import logging
from django.core.mail import EmailMessage, send_mail

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin

from .serializers import ClaimSerializer
from .models import Claim
from django.core.mail import send_mail
import json
import ast
from django.conf import settings


class ReportClaim(GenericAPIView, CreateModelMixin, ListModelMixin):
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        claim = serializer.save()
        # Send email
        subject = f'New Claim Reported by {claim.email}'
        message = f"Insured: {claim.insured}\nPolicy Number: {claim.policy_number}\nEmail: {claim.email}\nPhone: {claim.phone}"

        # try:
        #     send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER,
        #               recipient_list=['davidedetnsikak@gmail.com'], fail_silently=False)
        #     print("Mail Sent Successfully")
        # except Exception as e:
        #     print("error sending mail", e)

        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            ['davidedetnsikak@gmail.com']  # Replace with the recipient's email
        )

        if claim.file:
            email.attach(claim.file.name, claim.file.read(),

                         )

        email.send(fail_silently=False)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
