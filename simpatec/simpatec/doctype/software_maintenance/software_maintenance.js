// Copyright (c) 2023, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Software Maintenance', {
    refresh(frm) {
        var reoccurring_label = __(`${frm.doc.licence_renewal_via} (Reoccurring Maintenance)`)
        frm.add_custom_button(reoccurring_label, function () {
            frm.events.make_reoccurring(frm)
        }, __("Create"));


        //hide all + in the connection
        $('.form-documents button').hide();
    },
    make_reoccurring(frm){
        frappe.call({
            method: "simpatec.simpatec.doctype.software_maintenance.software_maintenance.make_reoccuring_sales_order",
            args: {
                software_maintenance: frm.doc.name,
                is_background_job: 0,
                licence_renewal_via: frm.doc.licence_renewal_via
            },
            callback: function (r) {
            },
        });
    }
});

frappe.ui.form.on('Software Maintenance Item', {
    item_code(frm, cdt, cdn){
        var item = frappe.get_doc(cdt, cdn);
        item.pricing_rules = ''
        if (item.item_code && item.uom) {
            return frm.call({
                method: "erpnext.stock.get_item_details.get_conversion_factor",
                args: {
                    item_code: item.item_code,
                    uom: item.uom
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', r.message.conversion_factor);
                    }
                }
            });
        }
    },
});
