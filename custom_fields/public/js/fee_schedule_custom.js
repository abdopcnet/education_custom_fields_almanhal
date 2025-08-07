frappe.ui.form.on("Fee Structure", {
  refresh: function (frm) {
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button("Create Fee Schedules", function () {
        frappe.prompt(
          [
            {
              fieldname: "due_date",
              label: "تاريخ الاستحقاق",
              fieldtype: "Date",
              reqd: 1,
            },
          ],
          function (values) {
            if (!values.due_date) {
              frappe.msgprint("برجاء إدخال تاريخ الاستحقاق حتي يتم إنشاء جدولة مجمعة");
              return;
            }
            var grade_list = [];
            if (frm.doc.custom_grade_select && frm.doc.custom_grade_select.length) {
              frm.doc.custom_grade_select.forEach(function(row) {
                if (row.grade) {
                  grade_list.push(row.grade);
                }
              });
            }
            console.log("البرامج التي سيتم الإنشاء لها:", grade_list);
            frappe.call({
              method: "custom_fields.fee_schedule_custom.create_fee_schedules",
              args: {
                fee_structure: frm.doc.name,
                due_date: values.due_date,
                grade_list: grade_list,
              },
              callback: function (r) {
                if (!r.exc) {
                  frappe.msgprint({
                    message: r.message && r.message.message ? r.message.message : "تم الإنشاء بنجاح.",
                    indicator: 'green',
                    primary_action: {
                      label: 'تسجيل الجدولة المجمعة',
                      action: function() {
                        frappe.call({
                          method: "custom_fields.fee_schedule_custom.submit_fee_schedules",
                          args: {
                            fee_structure: frm.doc.name,
                            grade_list: grade_list
                          },
                          callback: function(submit_result) {
                            frappe.msgprint("تم تسجيل جميع الجدولات بنجاح.");
                            frm.reload_doc();
                          }
                        });
                      }
                    },
                    secondary_action: {
                      label: 'تركها كمسودة',
                      action: function() {
                        frappe.msgprint("تم ترك الجدولات كمسودة.");
                      }
                    }
                  });
                  frm.reload_doc();
                }
              },
            });
          },
          "إنشاء جدولة الرسوم",
          "إنشاء"
        );
      });
    }
  },
});
