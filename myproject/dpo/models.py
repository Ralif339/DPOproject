from django.db import models
from index.models import User

# Create your models here.
class CourseType(models.Model):
    type_name = models.CharField(max_length=255, verbose_name="Имя типа курса")
    
    
class Course(models.Model):
    course_name = models.CharField(max_length=255, verbose_name="Название курса")
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE, verbose_name="Тип курса")
    price = models.FloatField(verbose_name="Цена")
    hours_count = models.IntegerField(verbose_name="Количество часов")
    
    
class CommissionMember(models.Model):
    surname = models.CharField(max_length=255, verbose_name="Фамилия")
    name = models.CharField(max_length=255, verbose_name="Имя")
    patronymic = models.CharField(max_length=255, verbose_name="Отчество")
    position = models.CharField(max_length=255, verbose_name="Должность")
    
class StudentExpulsion(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Слушатель")
    reason = models.CharField(max_length=255, verbose_name="Причина")
    date = models.DateField(verbose_name="Дата")
    
class Teacher(models.Model):
    surname = models.CharField(max_length=255, verbose_name="Фамилия")
    name = models.CharField(max_length=255, verbose_name="Имя")
    patronymic = models.CharField(max_length=255, verbose_name="Отчество")
    position = models.CharField(max_length=255, verbose_name="Должность")
    
class Group(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название группы")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Преподаватель")
    begin_date = models.DateField(verbose_name="Дата начала")
    finish_date = models.DateField(verbose_name="Дата окончания")
    student = models.ManyToManyField(User, through="StudentGroup")
    commission = models.ManyToManyField(CommissionMember, through="GroupCommission")
    
class StudentGroup(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Слушатель")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")
    date = models.DateField(verbose_name="Дата зачисления")
    
class GroupCommission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")
    commission_member = models.ForeignKey(CommissionMember, on_delete=models.CASCADE, verbose_name="Член комиссии")
    role = models.CharField(max_length=128, verbose_name="Роль")
    
class Statements(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Слушатель")
    statement_type = models.CharField(max_length=128, verbose_name="Тип заявления")
    submitting_date = models.DateField(verbose_name="Дата подачи")