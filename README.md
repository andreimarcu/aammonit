aammonit
========

Stub of a simple python monitoring system


Requirements
------------
- Python 
- All dependencies in requirements.txt

Installation
------------
1. pip install -r requirements.txt
1. Copy config.py from config.py.example and edit for your usage
2. Run ./aammonit.py
3. Enjoy!


Ideas/Vision
------

Globally
- The concept is supposed to extend to any monitorable thing:
    - notify if price of bitcoin exceeds X
    - notify if outside temperature drops below X
    - notify if html page's DOM element changed
    - etc. 
- Create an interface class, that can control aammonit as a whole (dynamically add notifiers, services, stop, start, etc)
    - Subclasses of this can be a terminal controller, IRC/XMPP controller (but then have to re-use the notifier as a controller, so need a way to communicate).
    - Where/how is the configuration stored? sqlite? json overwrite on each config change/save? etc.
- *Maybe* introduce metering, save results of each check, make them available to access in the interfaces 
    - i.e. IRC/XMPP interface: 

    ```
    <user> .view service_check_1  
    <aammonit> Last metrics for service_check_1: 0.1 0.2 0.1 0.15    
    ```
    - Web interface would display graphs, etc.



Monitors
- Every monitor should be optionally threaded, with an individual interval of checking, for high importance service checks
- Add "retries" for checks until declared down
- Detect self-connectivity issues before saying that everything is down


ETC
---
- Due to the stub nature of this project, there are a lot of things to cover that aren't covered here.



Author
------
Andrei Marcu, http://andreim.net/