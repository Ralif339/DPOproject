from django.shortcuts import render, redirect, get_object_or_404
from index.models import User
from .models import *
from .forms import *
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, OuterRef, Subquery


def superuser_render(request, template: str, context=None):
    if request.user.is_superuser:
        if context:
            return render(request, template, context=context)
        else:
            return render(request, template)
    else:
        return redirect('index')


# Create your views here.
def students_view(request):
    students = User.objects.all().filter(is_superuser="False")
    for student in students:
        for groups in student.group_set.all():
            print(student.name, groups.name)
    return superuser_render(request, "dpo/students/students.html", context={"students": students})

def student_profile_view(request, student_id):
    student = User.objects.get(id=student_id)
    student_groups = StudentGroup.objects.filter(student=student).select_related('group')
    context = {
        "student": student,
        "student_groups": student_groups,  
        "today": timezone.now().date()
    }
    return render(request, 'dpo/students/student_profile.html', context)


def groups_view(request):
    # Подзапрос для подсчета отчисленных студентов в группе
    expelled_students = StudentExpulsion.objects.filter(
        group=OuterRef("id")
    ).values("group").annotate(count=Count("student")).values("count")

    # Получаем группы с количеством слушателей без отчисленных
    groups = Group.objects.annotate(
        student_count=Count("studentgroup") - Subquery(expelled_students, output_field=models.IntegerField())
    )

    return superuser_render(request, 'dpo/groups/groups.html', context={"groups": groups})

def group_detail_view(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == "POST":
        student = User.objects.get(id=request.POST.get("student_id"))
        reason = request.POST.get("reason")
        student_expulsion = StudentExpulsion.objects.create(student=student,
                                                            reason=reason,
                                                            date=timezone.now().date(),
                                                            group=group)
        student_expulsion.save()
    
    expelled_students = StudentExpulsion.objects.filter(group=group).values_list("student_id", flat=True)
    student_groups = StudentGroup.objects.filter(group=group).exclude(student_id__in=expelled_students).select_related("student").order_by("student__surname")
    student_count = student_groups.count()
    context ={"group": group, "student_groups": student_groups, "student_count": student_count}
    return render(request, 'dpo/groups/group_detail.html', context)

def finish_course(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        student_ids = request.POST.get("student_ids")

        if not student_ids:
            messages.error(request, "Ошибка: Не переданы ID студентов.")
            return redirect("group_detail", group_id=group.id)

        student_ids = eval(student_ids)  # Преобразуем строку JSON в список

        for student_id in student_ids:
            student = get_object_or_404(User, id=student_id)
            
            # Проверяем, не отчислен ли уже студент
            if not StudentExpulsion.objects.filter(student=student, group=group).exists():
                StudentExpulsion.objects.create(
                    student=student,
                    reason="Завершение курса",
                    date=timezone.now().date(),
                    group=group
                )

        messages.success(request, "Все студенты отчислены по причине завершения курса.")
        return redirect("group_detail", group_id=group.id)

    return redirect("group_detail", group_id=group.id)


def statements_view(request):
    today_date = timezone.now().date()
    if request.method == "POST":
        if request.POST.get("action_type") == "recall":
            statement = Statements.objects.get(id=request.POST.get("statement_id"))
            statement.status = "Отклонено"
            statement.save()
            return redirect("statements")
        else:
            if request.POST.get("selected_group"):
                group = Group.objects.get(id=request.POST.get("selected_group"))
                statement = Statements.objects.get(id=request.POST.get("statement_id"))
                ed_kind = request.POST.get("ed_kind")
                group.student.add(statement.student, through_defaults={"date": today_date, "ed_kind": ed_kind})
                statement.status = "Одобрено"
                statement.group = group
                statement.save()
            return redirect("statements")
        
    statements = Statements.objects.filter(status="На рассмотрении")
    groups = Group.objects.all()
    return superuser_render(request, 'dpo/statements.html', context={"statements": statements,
                                                                     "groups": groups,
                                                                     "today": today_date})


def commission_view(request):
    if request.method == "POST":
        member_id = request.POST.get('member_id')
        if member_id:
            member = CommissionMember.objects.get(id=member_id)
            member.delete()
            return redirect('commission')
    commission = CommissionMember.objects.all()
    return superuser_render(request, 'dpo/commission/commission.html', context={"commission": commission})


def orders_view(request):
    return superuser_render(request, 'dpo/orders.html')


def teachers_view(request):
    if request.method == "POST":
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher.delete()
            return redirect('teachers')
    teachers = Teacher.objects.all()
    return superuser_render(request, 'dpo/teachers/teachers.html', context={"teachers": teachers})

def teacher_edit_view(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = TeacherAddForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
        return redirect('teachers')
    form = TeacherAddForm(instance=teacher)
    context = {"form": form, "teacher": teacher}
    return render(request, 'dpo/teachers/teacher_edit.html', context)


def courses_view(request):
    if request.method == "POST":
        course = Course.objects.get(id=request.POST.get("course_id"))
        course.delete()
        return redirect('courses')
    courses = Course.objects.all()
    return superuser_render(request, 'dpo/courses/courses.html', context={"courses": courses})

def course_edit_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseAddForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
        return redirect('courses')
    form = CourseAddForm(instance=course)
    return render(request, 'dpo/courses/course_edit.html', {"form": form, "course": course})


def add_group_view(request):
    if request.method == "POST":
        form = GroupAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('groups')
    else:
        form = GroupAddForm()
    return superuser_render(request, 'dpo/groups/group_add.html', context={'form': form})


def add_course_view(request):
    if request.method == "POST":
        form = CourseAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseAddForm()
    return superuser_render(request, 'dpo/courses/course_add.html', context={'form': form,})


def add_teacher_view(request):
    if request.method == "POST":
        form = TeacherAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teachers')
    else:
        form = TeacherAddForm()
    return superuser_render(request, 'dpo/teachers/teacher_add.html', context={'form': form,})


def add_commission_view(request):
    if request.method == "POST":
        form = CommissionAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('commission')
    else:
        form = CommissionAddForm()
    return superuser_render(request, 'dpo/commission/commission_add.html', context={'form': form,})

def commission_edit_view(request, member_id):
    commission = get_object_or_404(CommissionMember, id=member_id)
    if request.method == "POST":
        form = CommissionAddForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
        return redirect('commission')
    form = CommissionAddForm(instance=commission)
    context = {"form": form, "commission": commission}
    return render(request, 'dpo/commission/commission_edit.html', context)