Getting Started
===============

The Python library can be installed using pip: ``pip install sax4bpm``

Prerequisites
*************

Before using this package, ensure that you have:

- Installed the required dependencies:

  - Python 3.9 or higher

- Set the following environment variables:
  
  - For usage of OpenAI models as the LLM for explainability integration:

    - ``OPENAI_KEY``: Your API key for accessing OpenAI services.

  - For usage of IBM GenAI as the LLM for explainability integration:

    - ``GENAI_KEY``: Your API key for accessing GenAI services.
    - ``GENAI_API``: Your API URL for accessing GenAI services.

  You can set these environment variables in your shell profile, like `.bashrc` or `.zshrc`, or through a `.env` file loaded by your application.

  Example:

  .. code-block:: bash

     export OPENAI_KEY="your-openai-api-key"

- To view the causal graphs, `Graphviz <https://graphviz.org/>`_ installation is required. The installation instructions can be found here: `Graphviz Download <https://graphviz.org/download/>`_. The path to the installed binaries should be added to the OS path.


Starting tips
*************

To get acquainted with the library we suggest you:

- Read the paper on causal discovery for business processes:   

  - `The WHY in Business Processes: Discovery of Causal Execution Dependencies <https://arxiv.org/abs/2310.14975>`_ .

- See examples on various usage scenarios supported by the library: 
  
  - :doc:`/tutorials`


.. toctree::  
   :maxdepth: 2
   :caption: Contents

