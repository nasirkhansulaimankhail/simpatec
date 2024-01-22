// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.provide("contact_set_control_panel")

frappe.query_reports["Contact Set Action Panel"] = {
	"filters": [
		{
			"fieldname":"contact_set",
			"label": __("Contact Set"),
			"fieldtype": "Link",
			"options": "Contact Set",
			"reqd": 1
		},
	],

	onload: async function (report) {
		$(".custom-actions").hide();
		// $(".standard-actions").hide();

		contact_set_control_panel.update_row_in_contact_set = function (contact_set, contact_set_row, notes, status) {
			frappe.call({
				method: "simpatec.simpatec.report.contact_set_action_panel.contact_set_action_panel.update_row_in_contact_set",
				args: {
					contact_set: contact_set,
					contact_set_row: contact_set_row,
					notes: notes,
					status: status
				},
				callback: function (r) {
					console.log(r.message.status)
					if (r.message && r.message.status === "updated") {
						frappe.ui.hide_open_dialog();
						report.refresh();
					}
				}
			})
		}

		getLogsHtml = function (contact_set, contact_set_row) {
			let rowLogInfoHtmlOutput = "";
			let html_segment = ""
			frappe.call({
				method: "simpatec.simpatec.report.contact_set_action_panel.contact_set_action_panel.get_row_log",
				args: {
					contact_set,
					contact_set_row
				},
				async: false,
				callback:  function (r) {
					let row_log = r.message;
					row_log.forEach(log => {
						let date = log["date"];
						let event = log["event"];
						let notes = log["notes"];
						let status = log["status"];
						if (date) {
							let status_html = (status) ? `<span >Status : ${status}</span>` : ``;	
							let notes_html = (notes) ? `<p class="pl-3">Notes : ${notes}</p>` : ``;	
							let divElement = `<div><p>${date} ${status_html}</p>${notes_html}</div>`;
							rowLogInfoHtmlOutput += divElement;
						}
					});

					if (rowLogInfoHtmlOutput) {
						html_segment =  `<div class="form-group" >
							<div class="clearfix">
								<label class="control-label" style="padding-right: 0px;"></label>
								<span class="help"></span>
							</div>
							<div class="like-disabled-input" style="height: 230px; overflow: auto;">${rowLogInfoHtmlOutput}</div>
						</div>`
					}
				}
			})
			return html_segment
		}

		getContactInfoHtml = function (contactInfo, field, linkType, label, contact_set, contact_set_row) {
			let contactInfoHtmlOutput = "";
			let html_segment = "";

			let linkPrefix = (linkType === "email") ? "mailto:" : "tel:";			
			contactInfo.forEach(infoObj => {
				let value = infoObj[field.toLowerCase()];
				let link = `${linkPrefix}${value}`;
				let notes = `Outdoing call on ${value}`
				let divElement = `<p><span><button type="button" class="btn btn-primary btn-sm"><a href="${link}" onclick="contact_set_control_panel.update_row_in_contact_set('${contact_set}', '${contact_set_row}', '${notes}')">📞</a></button></span><span>${value}</span></p>`;

				contactInfoHtmlOutput += divElement;
			});

			if (contactInfoHtmlOutput) {
				html_segment =  `<div class="form-group">
					<div class="clearfix">
						<label class="control-label" style="padding-right: 0px;">${label}</label>
						<span class="help"></span>
					</div>
					<div class="like-disabled-input">${contactInfoHtmlOutput}</div>
				</div>`
			}
			return html_segment
		}

		contact_set_control_panel.open_dialog = function (row) {
			let contact_set = (row["contact_set"] === "null") ? null : row["contact_set"];
			let contact_set_row = (row["contact_set_row"] === "null") ? null : row["contact_set_row"];
			let status = (row["status"] === "null") ? null : row["status"];
			let emails = (row["emails"] === "null") ? null : row["emails"];
			let phone_nos = (row["phone_nos"] === "null") ? null : row["phone_nos"];
			let first_name = (row["first_name"] === "null") ? null : row["first_name"];
			let last_name = (row["last_name"] === "null") ? null : row["last_name"];
			let contact_name = (first_name && last_name) ? `${first_name} ${last_name}` : first_name;

			let dialog = new frappe.ui.Dialog({
				title: "Take Action",
				// size: "large",
				 size: "extra-large",
				fields: [
					{
						label: "Contact Name",
						fieldname: "contact_name",
						fieldtype: "HTML",
						options: `<h3>${contact_name}</h3>`,
						read_only: 1
					},
					{
						label: "Email Address",
						fieldname: "email_address",
						fieldtype: "HTML",
						options: getContactInfoHtml(emails, "email_id", "email", "Emails", contact_set, contact_set_row),
						hidden: 1
					},
					{
						label: "Phone Nos",
						fieldname: "phone_nos",
						fieldtype: "HTML",
						options: getContactInfoHtml(phone_nos, "phone", "phone", "Phone Nos", contact_set, contact_set_row)
					},
					{
						fieldname: "colbreak1234",
						fieldtype: "Column Break"
					},
					{
						label: "Log Data",
						fieldname: "logs_data",
						fieldtype: "HTML",
						options: getLogsHtml(contact_set, contact_set_row)
					},
					{
						fieldname: "colbreak1235",
						fieldtype: "Column Break"
					},
					{
						label: "Status",
						fieldname: "status",
						fieldtype: "Select",
						options: "\nNew\nIn Work\nRejected\nOpportunity",
						default: status
					},
					{
						label: "Notes",
						fieldname: "notes",
						fieldtype: "Small Text"
					},
				],
				primary_action_label: "Update",
				primary_action() {
					var data = dialog.get_values();
					contact_set_control_panel.update_row_in_contact_set(contact_set, contact_set_row, data.notes, data.status);
					// dialog.hide();
				}
			});
			dialog.show();
		}
	}
};