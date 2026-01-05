"""
Authentication views for user registration, login, and session management.
Uses MongoDB for user storage and JWT for authentication.
"""

import bcrypt
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .mongodb_utils import get_users_collection
from .jwt_utils import create_jwt_token, get_user_from_request


class RegisterView(APIView):
    """Handle user registration."""
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        
        # Validation
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = get_users_collection()
        
        # Check if user already exists
        existing_user = users.find_one({'email': email})
        if existing_user:
            return Response(
                {'error': 'Email already registered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hash password with bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
        
        # Create user
        user_doc = {
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        result = users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Generate JWT token
        token = create_jwt_token(user_id, email)
        
        return Response({
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Handle user login."""
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = get_users_collection()
        user = users.find_one({'email': email})
        
        if not user:
            return Response(
                {'error': 'Invalid login credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return Response(
                {'error': 'Invalid login credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user_id = str(user['_id'])
        token = create_jwt_token(user_id, email)
        
        return Response({
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
            }
        })


class CurrentUserView(APIView):
    """Get current authenticated user."""
    
    def get(self, request):
        user = get_user_from_request(request)
        
        if not user:
            return Response(
                {'error': 'Not authenticated'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            'user': {
                'id': user['user_id'],
                'email': user['email'],
            }
        })
