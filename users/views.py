from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, OrganisationSerializer
from .models import User, Organisation
import uuid
import jwt, datetime

 
# Create your views here.
class RegisterView(APIView):
    def post(self, request):    
        serializer = UserSerializer(data= request.data)
        serializer.is_valid(raise_exception= True)
        user = serializer.save()
        organisation = Organisation.objects.create(
            orgId = str(uuid.uuid4()),
            name=f"{user.firstName}'s Organisation",
            description = f"This is default organisation"
        )
        organisation.users.add(user)
        organisation.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email=request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()
        
        failed_login = {'status' : 'Bad request',
                        'message' : 'Authentication Failed',
                        'statusCode': status.HTTP_401_UNAUTHORIZED}
        if user is None:
            raise AuthenticationFailed(f'{failed_login}')
        if not user.check_password(password):
            raise AuthenticationFailed(f'{failed_login}')    
        payload = {
            'id': user.id,
            'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()
        }
        #.decode('utf-8'),https://stackoverflow.com/questions/65798281/attributeerror-str-object-has-no-attribute-decode-python-error 
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            "status":'success',
            'message':'Login successful',
            'data': {
                'accessToken' : token,
                'user':UserSerializer(user).data
            }
        } 
        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id = payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

 
class OrganisationListView(APIView):
    def get(self, request):
        organisations = Organisation.objects.all()
        serializer=OrganisationSerializer(organisations, many=True)
        return JsonResponse({"organisation": serializer.data})

class OrganisationsView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        organisations = Organisation.objects.filter(users__id=user.id).distinct()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({'status': 'success', 'message': 'Organisations retrieved successfully', 'data': serializer.data})

class OrganisationDetailView(APIView):
    def get(self, request, orgId):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        organisation = Organisation.objects.filter(orgId=orgId, users__id=user.id).first()
        if organisation is None:
            return Response({'status': 'Bad request', 'message': 'Organisation not found or access denied', 'statusCode': status.HTTP_404_NOT_FOUND})
        serializer = OrganisationSerializer(organisation)
        return Response({'status': 'success', 'message': 'Organisation details retrieved', 'data': serializer.data})


class CreateOrganisationView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        data = request.data
        if 'name' not in data or not data['name']:
            return Response({'status': 'Bad Request', 'message': 'Name is required', 'statusCode': status.HTTP_400_BAD_REQUEST})
        organisation = Organisation.objects.create(
            orgId=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description', '')
        )
        organisation.users.add(user)
        organisation.save()
        serializer = OrganisationSerializer(organisation)
        return Response({'status': 'success', 'message': 'Organisation created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class AddUserToOrganisationView(APIView):
    def post(self, request, orgId):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        organisation = Organisation.objects.filter(orgId=orgId, users__id=user.id).first()
        if organisation is None:
            return Response({'status': 'Bad request', 'message': 'Organisation not found or access denied', 'statusCode': status.HTTP_404_NOT_FOUND})
        userId = request.data.get('userId')
        if not userId:
            return Response({'status': 'Bad request', 'message': 'UserId is required', 'statusCode': status.HTTP_400_BAD_REQUEST})
        new_user = User.objects.filter(userId=userId).first()
        if new_user is None:
            return Response({'status': 'Bad request', 'message': 'User not found', 'statusCode': status.HTTP_404_NOT_FOUND})
        organisation.users.add(new_user)
        organisation.save()
        return Response({'status': 'success', 'message': 'User added to organisation successfully'}, status=status.HTTP_200_OK)

class UserDetailView(APIView):
    def get(self, request, id):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        target_user = User.objects.filter(id=id).first()
        if target_user is None:
            return Response({'status': 'Bad request', 'message': 'User not found', 'statusCode': status.HTTP_404_NOT_FOUND})
        serializer = UserSerializer(target_user)
        return Response({'status': 'success', 'message': 'User details retrieved', 'data': serializer.data})


class LogoutView(APIView):
    def post(self, request):
        response = Response() 
        response.delete_cookie('jwt')
        response.data = {
            'message' : 'success'
        }
        return response