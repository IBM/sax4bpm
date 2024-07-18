Process Data package
=========================
The package contains classes for data containers for different modules and their corresponding perpsectives:

* base class :class:`sax.process_data.data.BaseProcessDataObject` serving as base;
* :class:`sax.process_data.raw_event_data.RawEventData` representing a raw process event data log, each row in the dataframe representing single activity in the process and its attributes, useful for process mining; 
* :class:`sax.process_data.tabular_data.TabularEventData` representing a tabular view into the event log, each row representing a single trace for single process case. This representation is useful for causal execution dependency discovery. 

Additionally the package contains a base class for data representation of discovery results :class:`sax.process_data.discovery_result.ResultInfo` extended by process and causal discovery modules
The package also contains a sub-package with different formatters implementation - allowing to process standard file formats of event logs (XES,MXML and CSV) into data objects.

Subpackages
-----------

.. toctree::
   :maxdepth: 1

   sax.core.process_data.formatters

Submodules
----------

sax.core.process\_data.data module
----------------------------------

.. automodule:: sax.core.process_data.data
   :members:
   :undoc-members:
   :show-inheritance:

sax.core.process\_data.discovery\_result module
-----------------------------------------------

.. automodule:: sax.core.process_data.discovery_result
   :members:
   :undoc-members:
   :show-inheritance:

sax.core.process\_data.raw\_event\_data module
----------------------------------------------

.. automodule:: sax.core.process_data.raw_event_data
   :members:
   :undoc-members:
   :show-inheritance:

sax.core.process\_data.tabular\_data module
-------------------------------------------

.. automodule:: sax.core.process_data.tabular_data
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: sax.core.process_data
   :members:
   :undoc-members:
   :show-inheritance:
