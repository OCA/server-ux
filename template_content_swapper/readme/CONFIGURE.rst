Go to *Settings > Technical > User Interface > Template Content Mappings* to
create/maintain records.

Following fields should be filled in:

* **Report** (optional): Report record that includes the string you'd like to replace.
  Setting a report record will automatically update the template field.
* **Template** (required): The main QWeb template (ir.ui.view record) that includes the
  string you'd like to replace.
* **Domain** (optional): Domain used to restrict the records this configuration
  applies to. This option is only available for report configurations. Example:
  [('partner_id', '=', 1)]
* **Language** (optional): Target language for string replacement. If left blank, the
  replacement will be applied to all languages.
* **Content From** (required): An existing string to be replaced.
* **Content To** (optional): A new string to replace the existing string.

As a limitation, domain-based configurations that change content outside the article
section (for example, header or footer content) only work when printing a single
record. When multiple records are printed in one batch, those domain conditions are
not applied to the header/footer and only affect the article content.
