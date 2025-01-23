To use mulit_search you must put an "/" before the value you want to search. 
like this "/Kelly perry hart"
Do not put a separator between the first value and "/".

* Before:
  searching "/kelly|perry;hart" in employee, will give a none result.

.. image:: ../static/description/img/Before_multi_search.png 

* After:
  Searching "/kelly|perry;hart" in employee, will give "Kelly", "Perry"
  and "Hart"

.. image:: ../static/description/img/After_multi_search.png 
