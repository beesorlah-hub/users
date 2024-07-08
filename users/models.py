from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
import uuid

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, userId, firstName, lastName, email, password = None, phone = None):
        if not email:
            raise ValidationError('User must have an email address.')
        user = self.model(
            userId = userId,
            firstName = firstName,
            lastName = lastName,
            email = self.normalize_email(email),
            phone = phone,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, firstName, lastName, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            firstName= firstName,
            lastName= lastName,
        )
        user.is_admin = True
        user.is_active = True
        # user.is_staff = False
        user.is_superadmin = True
        user.save(using = self._db)
        return user

class User(AbstractBaseUser):
    userId = models.CharField(max_length= 225, unique=True, default=uuid.uuid4)
    firstName = models.CharField(max_length= 225, null= False)
    lastName = models.CharField(max_length= 225, null= False)
    email = models.EmailField(max_length= 225, unique=True, null = False)
    phone = models.CharField(max_length= 225, null= True, blank= True)
    password = models.CharField(max_length= 225, null= True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True    

    @property
    def is_staff(self):
        return self.is_admin

class Organisation(models.Model):
    orgId = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='organisations') 

    def __str__(self):
        return self.name