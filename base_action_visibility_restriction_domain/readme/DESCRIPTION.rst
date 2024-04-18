Using restriction records you can create domains for different groups. Domain will allow/deny action run on specific target model records.

If all restrictions of an action are without domain - action is hidden based on group (base_action_visibility_restriction behaviour).

If at least one restriction with domain - action is shown. Access will be defined once user run action.

If restriction record without domain - user can't run action. If with domain - domain defines for which records user (users group) can run action.
