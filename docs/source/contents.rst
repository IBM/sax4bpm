Contents
========
The following page provides entry point for documentation of all available functionality in the SAX4BPM library. The functionality can be divided into several logical layers: 

* the data layer, providing methods for importing event log in various standard formats (CSV, MXML, XES) and creating a data object :class:`sax.process_data.raw_event_data.RawEventData` representing the formatted event log. This event log data object can be utilized in various analysis layers for different views into the process, whether it is the process mining, causal discovery or XAI analysis;
* The process mining layer provides various functionalities for discovering process models and variants of the event log;
* The causal discovery layer allows to transpose the data object into tabular format and apply causal discovery algorithms;


1. Process Data Layer
	- :doc:`Process Data <sax.core.process_data>`
	- :doc:`Formatters <sax.core.process_data.formatters>`		

2. Causal Process Discovery
	- :doc:`Causal discovery library <sax.core.causal_process_discovery>`	
	- :doc:`Modalities <sax.core.causal_process_discovery.modalities>`			
	- :doc:`Causal discovery algorithms <sax.core.causal_process_discovery.algorithms>`
	- :doc:`Prior Knowledge <sax.core.causal_process_discovery.prior_knowledge>`

3. Process Mining
	- :doc:`Process Mining  <sax.core.process_mining>`

4. Synthethis
	- :doc:`LLM blending  <sax.core.synthesis>`
	- :doc:`LLMs Wrappers <sax.core.synthesis.llms>`
	- :doc:`RAG retreivers <sax.core.synthesis.rag>`


	
		

	
