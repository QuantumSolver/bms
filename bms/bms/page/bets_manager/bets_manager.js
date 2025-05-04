frappe.pages["bets-manager"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Bets Manager"),
		single_column: true,
	});
};

frappe.pages["bets-manager"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("bets_manager.bundle.js").then(() => {
		frappe.bets_manager = new frappe.ui.BetsManager({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}