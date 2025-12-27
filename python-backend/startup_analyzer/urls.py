"""
URL configuration for startup_analyzer project.
"""

from django.urls import path, include

urlpatterns = [
    path('', include('analyzer.urls')),
]
