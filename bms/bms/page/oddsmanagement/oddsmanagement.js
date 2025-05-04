frappe.pages["oddsmanagement"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Odds Management"),
		single_column: true,
	});
};

frappe.pages["oddsmanagement"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("oddsmanagement.bundle.js").then(() => {
		frappe.oddsmanagement = new frappe.ui.Oddsmanagement({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}