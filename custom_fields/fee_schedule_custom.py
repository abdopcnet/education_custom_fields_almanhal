import frappe
import json

@frappe.whitelist()
def create_fee_schedules(fee_structure, due_date, grade_list=None):
    """Create multiple Fee Schedules for all grades in grade_list"""
    if not fee_structure:
        frappe.throw("Fee Structure is required")
    if not due_date:
        frappe.throw("برجاء إدخال تاريخ الاستحقاق حتي يتم إنشاء جدولة مجمعة")
    validate_due_date(due_date)
    if not grade_list:
        frappe.throw("لم يتم إرسال أي برامج")
    if isinstance(grade_list, str):
        grade_list = json.loads(grade_list)
    doc = frappe.get_doc("Fee Structure", fee_structure)
    created_records = 0
    for grade in grade_list:
        if not grade:
            continue
        fee_schedule = frappe.new_doc("Fee Schedule")
        fee_schedule.fee_structure = fee_structure
        fee_schedule.program = grade
        fee_schedule.due_date = due_date
        # جلب بيانات البرنامج والسنة والفصل من Fee Structure أو من الصف الحالي حسب الحاجة
        program = grade
        academic_year = doc.academic_year
        academic_term = doc.academic_term
        # جلب جميع Student Groups المطابقة
        student_groups = frappe.get_all(
            "Student Group",
            filters={
                "program": program,
                "academic_year": academic_year,
                "academic_term": academic_term,
                "disabled": 0
            },
            fields=["name"]
        )
        for group in student_groups:
            fee_schedule.append("student_groups", {
                "student_group": group.name
            })
        for component in doc.components:
            fee_schedule.append("components", {
                "fees_category": component.fees_category,
                "description": component.description,
                "amount": component.amount,
                "total": component.amount
            })
        fee_schedule.insert()
        created_records += 1
    frappe.publish_realtime(
        "fee_schedule_progress",
        {"progress": 100, "reload": 1},
        user=frappe.session.user,
    )
    return {
        "message": f"تم إنشاء {created_records} جدولة رسوم بنجاح لجميع الصفوف.",
        "created_count": created_records
    }


@frappe.whitelist()
def submit_fee_schedules(fee_structure, grade_list=None):
    """Submit all Fee Schedules created for the given Fee Structure and grades"""
    if not fee_structure:
        frappe.throw("Fee Structure is required")
    if not grade_list:
        frappe.throw("لم يتم إرسال أي برامج")
    if isinstance(grade_list, str):
        grade_list = json.loads(grade_list)
    submitted = 0
    for grade in grade_list:
        if not grade:
            continue
        # ابحث عن جميع Fee Schedules المطابقة
        schedules = frappe.get_all(
            "Fee Schedule",
            filters={
                "fee_structure": fee_structure,
                "program": grade,
                "docstatus": 0
            },
            fields=["name"]
        )
        for sch in schedules:
            doc = frappe.get_doc("Fee Schedule", sch.name)
            doc.submit()
            submitted += 1
    return {
        "message": f"تم تسجيل {submitted} جدولة رسوم بنجاح.",
        "submitted_count": submitted
    }


def validate_due_date(due_date):
    if due_date < frappe.utils.nowdate():
        frappe.throw(
            _(f"Due Date {due_date} should be greater than or same as today's date.")
        )
