This module allows mulit_searching for all search.
For that, it add code before the search function.

It will allow you to search for multiple values separated by the character you
have configured.
* It will split the value like this:
[("name", "ilike","/Hart|perry;kelly")] => ['|', '|', '|', '|', '|' ("name", "ilike","Hart|perry;kelly"), ("name", "ilike","Hart|perry"), ("name", "ilike","Hart"), ("name", "ilike","perry;kelly"), ("name", "ilike","kelly"), ("name", "ilike","kelly"), ("name", "ilike", "/Hart|perry;kelly")]
