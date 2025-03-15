import docx
from .models import *
import io
from django.http import HttpResponse
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def set_font(paragraph, pt: float, ):
    for run in paragraph.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(pt)
        
def replace_text(paragraph, old_text: str, new_text: str, pt: float):
    paragraph.text = paragraph.text.replace(old_text, new_text)
    set_font(paragraph, pt)

def get_enroll_docx(group_id, number, date):
    group = Group.objects.get(id=group_id)
    expelled_students = StudentExpulsion.objects.filter(group=group).values_list("student_id", flat=True)
    student_groups = StudentGroup.objects.filter(group=group).exclude(student_id__in=expelled_students).select_related("student").order_by("student__surname")
    document = docx.Document('dpo/docs_patterns/enroll.docx')
    table1 = document.tables[0]
    table1.cell(1, 0).text = number
    table1.cell(1, 1).text = date
    for cell in table1.rows[1].cells:
        for run in cell.paragraphs[0].runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = document.paragraphs[9]
    match group.course.course_type:
        case "Профессиональная переподготовка":
            replace_text(p, "<CourseType>", "программе профессиональной подготовки", 11)
        case "Курсы повышения квалификации КПК":
            replace_text(p, "<CourseType>", "программе повышения квалификации КПК", 11)            
        case "Общеобразовательные программы для детей и взрослых":
            replace_text(p, "<CourseType>", "общеобразовательной программе для детей и взрослых", 11)            
        case "Профессиональное обучение":
            replace_text(p, "<CourseType>", "программе профессионального обучения", 11)
    replace_text(p, "<CourseName>", group.course.course_name, 11)
    p = document.paragraphs[11]
    replace_text(p, "<GroupName>", group.name, 12)
    for run in p.runs:
        run.bold = True
    p = document.paragraphs[12]
    replace_text(p, "<Cost>", f"{group.course.price}", 11)
    p = document.paragraphs[14]
    replace_text(p, "<TeacherName>", f"{group.teacher.surname} {group.teacher.name[0]}. {group.teacher.patronymic[0]}.", 11)
    table2 = document.tables[1]
    i = 1
    for student_group in student_groups:
        row = table2.add_row()
        row.cells[0].text = f"{i}."
        row.cells[1].text = f"{student_group.student.surname} {student_group.student.name} {student_group.student.patronymic}"
        if student_group.ed_kind == "Внебюджет":
            row.cells[2].text = "ВБС"
        for cell in row.cells:
            for run in cell.paragraphs[0].runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)
        i += 1
    
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="enroll_order_{group.name}.docx"'
    
    return response

