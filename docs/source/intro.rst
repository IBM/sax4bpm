
Introduction
============

``SAX4BPM`` is a high-level OO Python package which aims to provide an easy and intuitive way of exploring various perspectives into your business-process,such as mining process event
logs and discovering process model, which in turns drives causal-execution dependency discovery of causal relationships between process activities. This can provide the user more elaborate
picture into which activities actually affect execution of the other activities in the process. Additionally the causal execution dependency model can drive the explainability of various outcomes
of decisions made within the scope of the business processes and provide more precise view on feature dependency of those decisions.
To bring it all together we will integrate all perspectives together using LLMs (Large Language Model) to construct single human-interpretable view into explainations of various process decision
and outcomes.
The current causal module implementation relies on techniques and methods described in <>

Motivation
**********
A crucial element in analyzing the business process outcomes, making informed decisions on process adaptations and improvements is the genuine understanding of current state of affairs - getting sound and true explanations on the factors driving the current process outcomes and decisions made at various points of the 
business process execution. This entails understanding the true relationships between the execution of process activities, understanding how those relationships are affected by and affect various features of the business process,
and how those are integrated together to provide clear and sound explanations.

This package is intended to provide a one-place for gaining various perspectives into your business process activities relationship and explainability and such an integrated higher-level synthesis explainability view.

Limitations and Acknowledgments
*********************************

- To gain the process model perspective from process event logs, we rely on `PM4PY <https://pm4py-source.readthedocs.io/en/stable/pm4py.html>`_ Python package implementation, and wrap it with additional functionality in our  :class:`sax.process_data` module.

- The current package implementation includes the process discovery and causal discovery modules. In the nearest future we plan to extend it with XAI module and integrated view using LLMs.

.. toctree::  
   :maxdepth: 2
   :caption: Contents