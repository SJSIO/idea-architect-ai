from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project
from .serializers import (
    ProjectSerializer,
    AnalyzeRequestSerializer,
    AnalyzeResponseSerializer,
)
from .langgraph_workflow import run_analysis


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Project objects.
    
    Provides CRUD operations for startup analysis projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    

class AnalyzeView(APIView):
    """
    API endpoint to analyze a startup idea using the LangGraph multi-agent workflow.
    
    POST /analyze
    {
        "startupIdea": "Your startup idea description",
        "targetMarket": "Optional target market",
        "projectId": "Optional existing project UUID"
    }
    """
    
    def post(self, request):
        # Validate request
        serializer = AnalyzeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        startup_idea = serializer.validated_data['startupIdea']
        target_market = serializer.validated_data.get('targetMarket')
        project_id = serializer.validated_data.get('projectId')
        
        print(f"📊 Starting analysis for: {startup_idea[:100]}...")
        
        try:
            # Run the LangGraph workflow
            analysis_result = run_analysis(startup_idea, target_market)
            
            print("✅ Analysis complete!")
            
            # Format response to match frontend expectations
            response_data = {
                "success": True,
                "projectId": str(project_id) if project_id else None,
                "analysis": {
                    "marketAnalysis": analysis_result["market_analysis"],
                    "costPrediction": analysis_result["cost_prediction"],
                    "businessStrategy": analysis_result["business_strategy"],
                    "monetization": analysis_result["monetization"],
                    "legalConsiderations": analysis_result["legal_considerations"],
                    "techStack": analysis_result["tech_stack"],
                    "strategistCritique": analysis_result["strategist_critique"],
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "healthy"})


@api_view(['GET'])
def api_root(request):
    """API root endpoint."""
    return Response({
        "message": "Startup Analyzer API - Django + LangGraph Backend",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze",
            "projects": "/projects",
            "health": "/health",
        }
    })
