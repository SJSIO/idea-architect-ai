"""
Project CRUD views using MongoDB.
All operations verify user ownership via JWT.
"""

from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .mongodb_utils import get_projects_collection
from .jwt_utils import get_user_from_request


def serialize_project(project: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    return {
        'id': str(project['_id']),
        'user_id': project.get('user_id'),
        'startup_idea': project.get('startup_idea'),
        'target_market': project.get('target_market'),
        'market_analysis': project.get('market_analysis'),
        'cost_prediction': project.get('cost_prediction'),
        'business_strategy': project.get('business_strategy'),
        'monetization': project.get('monetization'),
        'legal_considerations': project.get('legal_considerations'),
        'tech_stack': project.get('tech_stack'),
        'strategist_critique': project.get('strategist_critique'),
        'status': project.get('status', 'pending'),
        'created_at': project.get('created_at', datetime.utcnow()).isoformat() + 'Z',
        'updated_at': project.get('updated_at', datetime.utcnow()).isoformat() + 'Z',
    }


class ProjectListCreateView(APIView):
    """List user's projects or create a new one."""
    
    def get(self, request):
        """List all projects for the authenticated user."""
        user = get_user_from_request(request)
        if not user:
            return Response(
                {'error': 'Unauthorized'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        projects = get_projects_collection()
        user_projects = list(
            projects.find({'user_id': user['user_id']})
            .sort('created_at', -1)
        )
        
        return Response([serialize_project(p) for p in user_projects])
    
    def post(self, request):
        """Create a new project."""
        user = get_user_from_request(request)
        if not user:
            return Response(
                {'error': 'Unauthorized'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        startup_idea = request.data.get('startup_idea', '').strip()
        target_market = request.data.get('target_market', '').strip() or None
        
        if not startup_idea:
            return Response(
                {'error': 'Startup idea is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        projects = get_projects_collection()
        now = datetime.utcnow()
        
        project_doc = {
            'user_id': user['user_id'],
            'startup_idea': startup_idea,
            'target_market': target_market,
            'market_analysis': None,
            'cost_prediction': None,
            'business_strategy': None,
            'monetization': None,
            'legal_considerations': None,
            'tech_stack': None,
            'strategist_critique': None,
            'status': 'pending',
            'created_at': now,
            'updated_at': now,
        }
        
        result = projects.insert_one(project_doc)
        project_doc['_id'] = result.inserted_id
        
        return Response(serialize_project(project_doc), status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    """Get, update, or delete a specific project."""
    
    def get_project_or_404(self, project_id: str, user_id: str):
        """Helper to get project with ownership check."""
        try:
            oid = ObjectId(project_id)
        except InvalidId:
            return None, Response(
                {'error': 'Invalid project ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        projects = get_projects_collection()
        project = projects.find_one({'_id': oid, 'user_id': user_id})
        
        if not project:
            return None, Response(
                {'error': 'Project not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return project, None
    
    def get(self, request, project_id):
        """Get a single project."""
        user = get_user_from_request(request)
        if not user:
            return Response(
                {'error': 'Unauthorized'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        project, error = self.get_project_or_404(project_id, user['user_id'])
        if error:
            return error
        
        return Response(serialize_project(project))
    
    def put(self, request, project_id):
        """Update a project."""
        user = get_user_from_request(request)
        if not user:
            return Response(
                {'error': 'Unauthorized'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        project, error = self.get_project_or_404(project_id, user['user_id'])
        if error:
            return error
        
        # Build update document
        update_fields = {}
        allowed_fields = [
            'startup_idea', 'target_market', 'status',
            'market_analysis', 'cost_prediction', 'business_strategy',
            'monetization', 'legal_considerations', 'tech_stack', 'strategist_critique'
        ]
        
        for field in allowed_fields:
            if field in request.data:
                update_fields[field] = request.data[field]
        
        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            
            projects = get_projects_collection()
            projects.update_one(
                {'_id': ObjectId(project_id)},
                {'$set': update_fields}
            )
        
        # Return updated project
        projects = get_projects_collection()
        updated = projects.find_one({'_id': ObjectId(project_id)})
        return Response(serialize_project(updated))
    
    def delete(self, request, project_id):
        """Delete a project."""
        user = get_user_from_request(request)
        if not user:
            return Response(
                {'error': 'Unauthorized'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        project, error = self.get_project_or_404(project_id, user['user_id'])
        if error:
            return error
        
        projects = get_projects_collection()
        projects.delete_one({'_id': ObjectId(project_id)})
        
        return Response({'success': True}, status=status.HTTP_200_OK)
