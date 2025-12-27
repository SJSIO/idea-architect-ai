from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    
    class Meta:
        model = Project
        fields = [
            'id',
            'startup_idea',
            'target_market',
            'market_analysis',
            'cost_prediction',
            'business_strategy',
            'monetization',
            'legal_considerations',
            'tech_stack',
            'strategist_critique',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'market_analysis',
            'cost_prediction',
            'business_strategy',
            'monetization',
            'legal_considerations',
            'tech_stack',
            'strategist_critique',
            'status',
            'created_at',
            'updated_at',
        ]


class AnalyzeRequestSerializer(serializers.Serializer):
    """Serializer for analyze endpoint request."""
    
    startupIdea = serializers.CharField(required=True)
    targetMarket = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    projectId = serializers.UUIDField(required=False, allow_null=True)


class AnalysisResultSerializer(serializers.Serializer):
    """Serializer for analysis results."""
    
    marketAnalysis = serializers.CharField()
    costPrediction = serializers.CharField()
    businessStrategy = serializers.CharField()
    monetization = serializers.CharField()
    legalConsiderations = serializers.CharField()
    techStack = serializers.CharField()
    strategistCritique = serializers.CharField()


class AnalyzeResponseSerializer(serializers.Serializer):
    """Serializer for analyze endpoint response."""
    
    success = serializers.BooleanField()
    projectId = serializers.UUIDField(allow_null=True)
    analysis = AnalysisResultSerializer()
    error = serializers.CharField(required=False, allow_null=True)
