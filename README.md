
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/server-ux&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/server-ux/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/server-ux/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/server-ux/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/server-ux/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/server-ux/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/server-ux)
[![Translation Status](https://translation.odoo-community.org/widgets/server-ux-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/server-ux-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# server-ux

Server side features for usability and user experience related.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[announcement](announcement/) | 17.0.1.0.1 |  | Notify internal users about relevant organization stuff
[barcode_action](barcode_action/) | 17.0.1.0.1 |  | Allows to use barcodes as a launcher
[base_cancel_confirm](base_cancel_confirm/) | 17.0.1.0.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Base Cancel Confirm
[base_export_manager](base_export_manager/) | 17.0.1.0.1 |  | Manage model export profiles
[base_import_security_group](base_import_security_group/) | 17.0.1.0.0 |  | Group-based permissions for importing CSV files
[base_menu_visibility_restriction](base_menu_visibility_restriction/) | 17.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Restrict (with groups) menu visibilty
[base_optional_quick_create](base_optional_quick_create/) | 17.0.1.0.0 |  | Avoid "quick create" on m2o fields, on a "by model" basis
[base_revision](base_revision/) | 17.0.1.0.0 |  | Keep track of revised document
[base_search_custom_field_filter](base_search_custom_field_filter/) | 17.0.1.0.0 | <a href='https://github.com/pedrobaeza'><img src='https://github.com/pedrobaeza.png' width='32' height='32' style='border-radius:50%;' alt='pedrobaeza'/></a> | Add custom filters for fields via UI
[base_substate](base_substate/) | 17.0.1.0.1 |  | Base Sub State
[base_technical_features](base_technical_features/) | 17.0.1.0.2 |  | Access to technical features without activating debug mode
[base_tier_validation](base_tier_validation/) | 17.0.4.1.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Implement a validation process based on tiers.
[base_tier_validation_formula](base_tier_validation_formula/) | 17.0.1.0.0 |  | Formulas for Base tier validation
[base_tier_validation_forward](base_tier_validation_forward/) | 17.0.2.0.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Forward option for base tiers
[base_tier_validation_server_action](base_tier_validation_server_action/) | 17.0.1.0.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Add option to call server action when a tier is validated
[date_range](date_range/) | 17.0.1.2.2 | <a href='https://github.com/lmignon'><img src='https://github.com/lmignon.png' width='32' height='32' style='border-radius:50%;' alt='lmignon'/></a> | Manage all kind of date range
[date_range_account](date_range_account/) | 17.0.1.0.0 | <a href='https://github.com/alexis-via'><img src='https://github.com/alexis-via.png' width='32' height='32' style='border-radius:50%;' alt='alexis-via'/></a> | Add Date Range menu entry in Invoicing app
[document_quick_access](document_quick_access/) | 17.0.1.0.0 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Document quick access
[mail_message_destiny_link_template](mail_message_destiny_link_template/) | 17.0.1.0.0 | <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> | Mail template to show destiny records in chatter.
[mail_suggested_recipient_unchecked](mail_suggested_recipient_unchecked/) | 17.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Mail suggested recipient unchecked
[multi_step_wizard](multi_step_wizard/) | 17.0.1.0.0 |  | Multi-Steps Wizards
[sequence_reset_period](sequence_reset_period/) | 17.0.1.0.0 |  | Auto-generate yearly/monthly/weekly/daily sequence period ranges
[server_action_mass_edit](server_action_mass_edit/) | 17.0.1.0.3 |  | Mass Editing

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
