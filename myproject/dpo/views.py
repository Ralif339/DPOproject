from django.shortcuts import render, redirect, get_object_or_404
from index.models import User
from .models import *
from .forms import *
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, OuterRef, Subquery
from student import forms as dpo_forms
from .doc_generation import *
from django.db.models import Q



def superuser_render(request, template: str, context=None):
    if request.user.is_superuser:
        if context:
            return render(request, template, context=context)
        else:
            return render(request, template)
    else:
        return redirect('index')


def students_view(request):
    students = User.objects.filter(is_superuser=False).prefetch_related(
        'studentgroup_set__group'
    )
    
    # Получаем параметры фильтрации из GET-запроса
    search_query = request.GET.get('search')
    status_filter = request.GET.get('status')
    ed_kind_filter = request.GET.get('ed_kind')
    birth_year_filter = request.GET.get('birth_year')
    
    # Применяем поиск по ФИО, СНИЛС, телефону или email
    if search_query:
        students = students.filter(
            Q(surname__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(patronymic__icontains=search_query) |
            Q(SNILS__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        ).distinct()
    
    # Применяем фильтры
    if status_filter:
        students = students.filter(
            studentgroup__group__status=status_filter
        ).distinct()
    
    if ed_kind_filter:
        students = students.filter(
            studentgroup__ed_kind=ed_kind_filter
        ).distinct()
    
    if birth_year_filter:
        students = students.filter(
            Q(birthday__year=birth_year_filter) | 
            Q(birthday__isnull=True)
        ).distinct()
    
    context = {
        "students": students,
        "status_choices": set(Group.objects.values_list('status', flat=True).distinct()),
        "ed_kind_choices": set(StudentGroup.objects.values_list('ed_kind', flat=True).distinct()),
        "search_query": search_query,
    }
    return superuser_render(request, "dpo/students/students.html", context)

def student_profile_view(request, student_id):
    student = User.objects.get(id=student_id)
    student_groups = StudentGroup.objects.filter(student=student).select_related('group')
    context = {
        "student": student,
        "student_groups": student_groups,  
        "today": timezone.now().date()
    }
    return superuser_render(request, 'dpo/students/student_profile.html', context)


from django.db.models import Q, Count, OuterRef
from django.shortcuts import render
from .models import Group, StudentExpulsion
from django.db.models.functions import Coalesce

def groups_view(request):
    # Подзапрос для отчисленных студентов (исключая завершивших обучение)
    expelled_students = StudentExpulsion.objects.filter(
        group=OuterRef("id")
    ).exclude(
        reason="Завершение курса"
    ).values("group").annotate(count=Count("student")).values("count")

    # Базовый запрос
    groups = Group.objects.annotate(
        student_count=Count("studentgroup") - Coalesce(Subquery(expelled_students), 0)
    ).select_related('course', 'teacher')

    # Получаем параметры фильтрации
    search = request.GET.get('search')
    course_type = request.GET.get('course_type')
    teacher = request.GET.get('teacher')
    status = request.GET.get('status')

    # Применяем фильтры
    if search:
        groups = groups.filter(
            Q(name__icontains=search) |
            Q(course__course_name__icontains=search)
        )

    if course_type:
        groups = groups.filter(course__course_type=course_type)

    if teacher:
        groups = groups.filter(teacher_id=teacher)

    if status:
        groups = groups.filter(status=status)

    # Подготовка контекста
    context = {
        'groups': groups,
        'teachers': Group.objects.values('teacher__id', 'teacher__surname', 'teacher__name').distinct(),
        'course_types': Group.objects.values_list('course__course_type', flat=True).distinct(),
        'statuses': Group.objects.values_list('status', flat=True).distinct(),
        'current_search': search,
        'current_course_type': course_type,
        'current_teacher': teacher,
        'current_status': status,
    }
    
    return superuser_render(request, 'dpo/groups/groups.html', context)

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
    
    group_commission = GroupCommission.objects.filter(group=group)
    
    has_commission = group_commission.exists()
    
    # Проверка наличия приказа о зачислении
    has_enrollment_order = Orders.objects.filter(group=group).exists()
    
    # Проверка наличия протокола экзамена
    has_exam_protocol = Protocols.objects.filter(group=group).exists()
    
    # Проверка статуса группы
    is_group_finished = group.status == "Обучение завершено"
    
    
    
    expelled_students = StudentExpulsion.objects.filter(reason="Завершение курса", group=group)
    student_groups = StudentGroup.objects.filter(group=group)
    students_ed_kind = []
    
    for student_group in student_groups:
        for expelled_student in expelled_students:
            if expelled_student.student.id == student_group.student.id:
                students_ed_kind.append((student_group.student, student_group.ed_kind))
                         
    expelled_students = StudentExpulsion.objects.filter(group=group).values_list("student_id", flat=True)
    student_groups = StudentGroup.objects.filter(group=group).exclude(student_id__in=expelled_students).select_related("student").order_by("student__surname")
    expelled_students = StudentExpulsion.objects.filter(group=group)
    context ={
        "group": group, 
        "student_groups": student_groups, 
        "group_commission": group_commission,
        "has_commission": has_commission,
        "has_enrollment_order": has_enrollment_order,
        "has_exam_protocol": has_exam_protocol,
        "is_group_finished": is_group_finished,
        "students_ed_kind": students_ed_kind,
        "expelled_students": expelled_students,
    }
    return superuser_render(request, 'dpo/groups/group_detail.html', context)

def edit_group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == "POST":
        form = GroupAddForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные группы успешно обновлены")
            return redirect('group_detail', group_id=group.id)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        form = GroupAddForm(instance=group)
    
    context = {
        'form': form,
        'group': group,
    }
    return superuser_render(request, 'dpo/groups/group_edit.html', context)

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
        group.status = "Обучение завершено"
        group.save()
        messages.success(request, "Все студенты отчислены по причине завершения курса.")
        return redirect("group_detail", group_id=group.id)

    return redirect("group_detail", group_id=group.id)

from django.template.defaulttags import register

@register.filter
def filter_group(groups, course):
    today = timezone.now().date()
    return [group for group in groups if group.finish_date > today and group.course.id == course.id]

def statements_view(request):
    today_date = timezone.now().date()
    
    if request.method == "POST":
        statement_id = request.POST.get("statement_id")
        statement = Statements.objects.get(id=statement_id)
        
        # Определяем какая кнопка была нажата
        if 'approve_btn' in request.POST:  # Была нажата кнопка "Одобрить"
            if statement.statement_type == "зачисление":
                group_id = request.POST.get("selected_group")
                if group_id:
                    group = Group.objects.get(id=group_id)
                    ed_kind = request.POST.get("ed_kind")
                    group.student.add(statement.student, through_defaults={"date": today_date, "ed_kind": ed_kind})
                    statement.status = "Одобрено"
                    statement.group = group
                    statement.save()
            elif statement.statement_type == "отчисление":
                statement.status = "Одобрено"
                statement.save()
        elif 'reject_btn' in request.POST:  # Была нажата кнопка "Отклонить"
            statement.status = "Отклонено"
            statement.save()
        
        return redirect("statements")
    
    # Фильтрация заявлений
    statements = Statements.objects.all()
    
    # Получаем параметры фильтрации
    search_query = request.GET.get('search')
    statement_type = request.GET.get('type')
    status = request.GET.get('status')
    course_id = request.GET.get('course')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Применяем фильтры
    if search_query:
        statements = statements.filter(
            Q(student__surname__icontains=search_query) |
            Q(student__name__icontains=search_query) |
            Q(student__patronymic__icontains=search_query))
    
    if statement_type:
        statements = statements.filter(statement_type=statement_type)
    
    if status:
        statements = statements.filter(status=status)
    
    if course_id:
        statements = statements.filter(course_id=course_id)
    
    if date_from:
        try:
            statements = statements.filter(submitting_date__gte=date_from)
        except:
            pass
    
    if date_to:
        try:
            statements = statements.filter(submitting_date__lte=date_to)
        except:
            pass
    
    # Подготовка данных для шаблона
    statements_list = []
    for statement in statements:
        suitable_groups = []
        has_suitable_groups = False
        
        if statement.status == "На рассмотрении" and statement.statement_type == "зачисление":
            suitable_groups = Group.objects.filter(
                finish_date__gt=today_date,
                course=statement.course
            )
            has_suitable_groups = suitable_groups.exists()
        
        statements_list.append({
            'statement': statement,
            'suitable_groups': suitable_groups,
            'has_suitable_groups': has_suitable_groups
        })
    
    # Получаем данные для фильтров
    courses = Course.objects.all()
    
    context = {
        'statements': statements_list,
        'courses': courses,
        'current_search': search_query,
        'current_type': statement_type,
        'current_status': status,
        'current_course': course_id,
        'current_date_from': date_from,
        'current_date_to': date_to,
    }
    
    return render(request, 'dpo/statements.html', context)


def commission_view(request):
    if request.method == "POST":
        member_id = request.POST.get('member_id')
        if member_id:
            member = CommissionMember.objects.get(id=member_id)
            member.delete()
            return redirect('commission')
    commission = CommissionMember.objects.all()
    return superuser_render(request, 'dpo/commission/commission.html', context={"commission": commission})


def documents_view(request):
    return superuser_render(request, 'dpo/documents/documents.html')


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
    return superuser_render(request, 'dpo/commission/commission_edit.html', context)


def student_edit_view(request, student_id):
    student = User.objects.get(id=student_id)
    if request.method == "POST":
        form = dpo_forms.StudentInfoForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('index')
    form = dpo_forms.StudentInfoForm(instance=student)
    return superuser_render(request, 'dpo/students/student_edit.html', context={"form": form,
                                                                          "student": student})
    
def enroll_order_view(request, group_id):
    groups = Group.objects.all()
    context = {"groups": groups, "group_id": group_id}
    if request.method == "POST":
        doc_number = request.POST.get('doc_number')
        date = request.POST.get("date")
        order, created = Orders.objects.get_or_create(
            date=date,
            number=doc_number,
            defaults={'group': Group.objects.get(id=group_id)}
        )
        response = get_enroll_docx(group_id, doc_number, date)
        return response
    return superuser_render(request, "dpo/documents/enroll_order.html", context=context)   

    
def commission_order_view(request, group_id):
    groups = Group.objects.all()
    context = {"groups": groups, "group_id": group_id,}
    if request.method == "POST":
        doc_number = request.POST.get('doc_number')
        date = request.POST.get("date")
        response = get_commission_docx(group_id, doc_number, date)
        return response
    return superuser_render(request, "dpo/documents/commission_order.html", context=context) 

def commission_group_add_view(request, group_id):
    group = Group.objects.get(id=group_id)
    members = CommissionMember.objects.all()
    if request.method == "POST":
        chairman = CommissionMember(id=request.POST.get("сhairman"))
        new_member = GroupCommission(group=group, commission_member=chairman, role="Председатель комиссии")
        new_member.save()
        
        deputy = CommissionMember(request.POST.get("deputy"))
        new_member = GroupCommission(group=group, commission_member=deputy, role="Заместитель председателя комиссии")
        new_member.save()
        
        secretary = CommissionMember(request.POST.get("secretary"))
        new_member = GroupCommission(group=group, commission_member=secretary, role="Секретарь")
        new_member.save()
        
        member = CommissionMember(request.POST.get("member"))
        new_member = GroupCommission(group=group, commission_member=member, role="Член комиссии")
        new_member.save()
        
        expelled_students = StudentExpulsion.objects.filter(group=group).values_list("student_id", flat=True)
        student_groups = StudentGroup.objects.filter(group=group).exclude(student_id__in=expelled_students).select_related("student").order_by("student__surname")
        student_count = student_groups.count()
        group_commission = GroupCommission.objects.filter(group=group)
        members = CommissionMember.objects.all()
        group_commission = GroupCommission.objects.filter(group=group)
    
        has_commission = group_commission.exists()
        
        # Проверка наличия приказа о зачислении
        has_enrollment_order = Orders.objects.filter(group=group).exists()
        
        # Проверка наличия протокола экзамена
        has_exam_protocol = Protocols.objects.filter(group=group).exists()
        
        # Проверка статуса группы
        is_group_finished = group.status == "Обучение завершено"
        context ={"group": group, "student_groups": student_groups, 
              "student_count": student_count, "group_commission": group_commission,
              "has_commission": has_commission,
              "has_enrollment_order": has_enrollment_order,
              "has_exam_protocol": has_exam_protocol,
              "is_group_finished": is_group_finished,}
        return superuser_render(request, 'dpo/groups/group_detail.html', context)
    
    
    
    context = {"group": group, "members": members, }
    return superuser_render(request, 'dpo/groups/commission_group_add.html', context=context)

def lesson_log_view(request, group_id):
    response = get_lesson_log_docx(group_id)
    return response

def protocol_view(request, group_id):
    context = {"group_id": group_id,}
    if request.method == "POST":
        doc_number = request.POST.get('doc_number')
        date = request.POST.get("date")
        protocol, created = Protocols.objects.get_or_create(
            date=date,
            number=doc_number,
            defaults={'group': Group.objects.get(id=group_id)}
        )
        print("Протокол", created)
        response = get_protocol_docx(group_id, doc_number, date)
        return response
    return superuser_render(request, "dpo/documents/protocol.html", context=context) 

def exam_sheet_view(request, group_id):
    orders = Orders.objects.filter(group=Group.objects.get(id=group_id))
    context = {"group_id": group_id, "orders": orders}
    if request.method == "POST":
        doc_number = request.POST.get('doc_number')
        date = request.POST.get("date")
        order = Orders.objects.get(id=request.POST.get("order_id"))
        response = get_exam_sheet_docx(group_id, doc_number, date, order)
        return response
    return superuser_render(request, "dpo/documents/exam_sheet.html", context=context)


def commission_group_edit_view(request, group_id):
    group = Group.objects.get(id=group_id)
    gc = GroupCommission.objects.filter(group=group)
    if request.method == "POST":
        for member in gc:
            match member.role:
                case "Председатель комиссии":  
                    chairman = CommissionMember(id=request.POST.get("сhairman"))
                    member.commission_member = chairman
                    member.save()
                case "Заместитель председателя комиссии":  
                    deputy = CommissionMember(id=request.POST.get("deputy"))
                    member.commission_member = deputy
                    member.save()
                case "Секретарь":  
                    secretary = CommissionMember(id=request.POST.get("secretary"))
                    member.commission_member = secretary
                    member.save()
                case "Член комиссии":  
                    com_member = CommissionMember(id=request.POST.get("member"))
                    member.commission_member = com_member
                    member.save()

        group_commission = GroupCommission.objects.filter(group=group)
        
        has_commission = group_commission.exists()
        
        # Проверка наличия приказа о зачислении
        has_enrollment_order = Orders.objects.filter(group=group).exists()
        
        # Проверка наличия протокола экзамена
        has_exam_protocol = Protocols.objects.filter(group=group).exists()
        
        # Проверка статуса группы
        is_group_finished = group.status == "Обучение завершено"
        expelled_students = StudentExpulsion.objects.filter(group=group).values_list("student_id", flat=True)
        student_groups = StudentGroup.objects.filter(group=group).exclude(student_id__in=expelled_students).select_related("student").order_by("student__surname")
        student_count = student_groups.count()
        group_commission = GroupCommission.objects.filter(group=group)
        context ={"group": group, "student_groups": student_groups, 
              "student_count": student_count,
              "group_commission": group_commission,
              "has_commission": has_commission,
              "has_enrollment_order": has_enrollment_order,
              "has_exam_protocol": has_exam_protocol,
              "is_group_finished": is_group_finished,}
        return superuser_render(request, 'dpo/groups/group_detail.html', context)
    
    members = CommissionMember.objects.all()
    context = {"group": group, "members": members}
    return superuser_render(request, 'dpo/groups/commission_group_edit.html', context=context)


def expel_group_view(request, group_id):
    protocols = Protocols.objects.filter(group=Group.objects.get(id=group_id))
    context = {"group_id": group_id, "protocols": protocols}
    if request.method == "POST":
        doc_number = request.POST.get('doc_number')
        date = request.POST.get("date")
        protocol = Protocols.objects.get(id=request.POST.get("protocol_id"))
        response = get_expel_group_order_docx(group_id, doc_number, date, protocol)
        return response
    return superuser_render(request, "dpo/documents/expel_group.html", context=context)