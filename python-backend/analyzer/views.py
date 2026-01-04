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
                "orchestrator": {
                    "selectedAgents": analysis_result.get("selected_agents", []),
                    "reasoning": analysis_result.get("orchestrator_reasoning", ""),
                    "startupCategory": analysis_result.get("startup_category", ""),
                    "complexityScore": analysis_result.get("complexity_score", 5),
                },
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
            "knowledge": "/knowledge",
            "knowledge_status": "/knowledge/status",
            "knowledge_locations": "/knowledge/locations",
            "api_keys_status": "/api-keys/status",
        }
    })


@api_view(['GET'])
def api_key_status(request):
    """Get status of configured Groq API keys."""
    from .api_key_manager import get_key_status
    
    try:
        status = get_key_status()
        return Response({
            "success": True,
            "status": status
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=500)


# =============================================================================
# Knowledge Base Management Endpoints
# =============================================================================

@api_view(['GET'])
def knowledge_status(request):
    """Get status of all knowledge bases."""
    from .rag_system import get_knowledge_base_status
    
    try:
        status = get_knowledge_base_status()
        return Response({
            "success": True,
            "status": status
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def knowledge_locations(request):
    """Get file upload locations for each agent's knowledge base."""
    from .rag_system import get_upload_locations
    
    try:
        locations = get_upload_locations()
        return Response({
            "success": True,
            "locations": locations
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def refresh_knowledge(request):
    """Refresh/reload knowledge bases."""
    from .rag_system import refresh_knowledge_base
    
    agent_type = request.data.get('agent_type')  # Optional: specific agent
    
    try:
        results = refresh_knowledge_base(agent_type)
        return Response({
            "success": True,
            "message": "Knowledge base refreshed successfully",
            "results": results
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
