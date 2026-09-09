To configure action visibility for a model:

1.  Activate developer mode.
2.  Go to *Settings \> Technical \> Database Structure \> Models*.
3.  Select the model for which you want to restrict actions.
4.  In the *View Action Visibility* section:
    - Add groups to *Duplicate Allowed Groups* to restrict the duplicate
      action in form views to only those groups. Leave empty to allow
      all users to duplicate.
    - Add groups to *Delete Allowed Groups* to restrict the delete
      action in form, list, and kanban views to only those groups. Leave
      empty to allow all users to delete.

Note: the restriction applies to every user who is not a member of the
allowed groups, administrators included. If you restrict an action to a
group you do not belong to, the button will be hidden for you as well.
Add yourself to the allowed group to keep access.
