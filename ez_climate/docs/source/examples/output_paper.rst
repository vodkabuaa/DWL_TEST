================================
Example of output from dlw-paper
================================

Below is an example from the DLW-paper, referred to as the base case.

First, we need to create an object of :class:`ez_climate.tree.TreeModel` with desicion times at 0, 15, 45, 85, 185, and 285 years from now. 

.. literalinclude:: ../code/output_paper.py
   :lines: 1-3


Next we create an :class:`ez_climate.bau.DLWBusinessAsUsual` object and set up the business as usual emission using the tree structure given by :attr:`t`.

.. literalinclude:: ../code/output_paper.py
   :lines: 5-8


We move on to create an :class:`ez_climate.cost.DLWCost` object using the base case parameters.

.. literalinclude:: ../code/output_paper.py
   :lines: 10-13

After this we are ready to create an :class:`ez_climate.damage.DLWDamage` object and simulate damages using the :func:`damage_simulation` method, again using the base case parameters.

.. literalinclude:: ../code/output_paper.py
   :lines: 15-19


We are now ready to initiate the :class:`ez_climate.utility.EZUtility` object using the above created objects.

.. literalinclude:: ../code/output_paper.py
   :lines: 21-23


Next step is to find the optimial mitigation plan using the optimization algorithms found in :mod:`ez_climate.optimization`, and print the Social Cost of Carbon (SCC) given by this mitigation plan.


.. literalinclude:: ../code/output_paper.py
   :lines: 26-37


**Putting it all together**


.. literalinclude:: ../code/output_paper.py
   :lines: 41-75
