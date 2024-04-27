// Copyright (c) 2023, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Software Maintenance', {
    refresh(frm) {
        frm.add_custom_button('Software Maintenance', function () { 
            frappe.call({
                method: "simpatec.events.sales_order.make_sales_order",
                args: {
                    software_maintenance: frm.doc.name,
                    is_background_job: 0
                },
                callback: function (r) {
                },
            });
        }, __("Create Sales Order"));


        frm.add_custom_button('Reoccuring Software Maintenance', function () {
            frappe.call({
                method: "simpatec.simpatec.doctype.software_maintenance.software_maintenance.make_sales_order",
                args: {
                    software_maintenance: frm.doc.name,
                    is_background_job: 0,
                    is_reoccuring: 1
                },
                callback: function (r) {
                },
            });
        }, __("Create Sales Order"));


        //hide all + in the connection
        $('.form-documents button').hide();
    }
});
