To create new announcements a user should be in the *Announcements Managers* group.
When your user has such permissions, this is the way to create an announcement:

#. Go to *Discuss > Announcements*
#. Create a new one and define a title. This title will be shown in the announcement
   header.
#. Define the announcement scope:

   - Specific users: manually select which users will see the announcement.
   - User groups: users from the selected groups will be the ones to see the
     announcement.
#. Define the announcement body. You can use rich formatting and event paste your
   own html (editor in debug mode).
#. By default, the announcement will be archived. This is to prevent the announcement
   to show up before time.
#. Once the announcement is ready, unarchive it going to the *Actions* menu an choosing
   the *Unarchive* option.
#. Optionally you can set an announcement date to schedule the announcement. The
   announcement won't show up until that date.
#. If the announcement doesn't make sense once a date is passed, you can set a due date.
   From that date, the announcement won't be shown to anyone.

There's a soft compatibility with OCA's `web_dialog_size` module. If the instance has
the module installed, you'll have the dialog resize controls by default in the
announcements. Additionally, you can show the announcement dialogs expanded to the
screen full width by default setting the system parameter key `announcement.full_size`
with to any value. Remove the parameter record to disable this behavior.
