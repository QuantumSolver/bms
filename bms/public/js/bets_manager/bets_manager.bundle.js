import { createApp } from "vue";
import App from "./App.vue";


class BetsManager {
	constructor({ page, wrapper }) {
		this.$wrapper = $(wrapper);
		this.page = page;

		this.init();
	}

	init() {
		this.setup_page_actions();
		this.setup_app();
	}

	setup_page_actions() {
		// setup page actions
	}

	setup_app() {
		// create a vue instance
		let app = createApp(App);
		// mount the app
		this.$bets_manager = app.mount(this.$wrapper.get(0));
	}
}

frappe.provide("frappe.ui");
frappe.ui.BetsManager = BetsManager;
export default BetsManager;