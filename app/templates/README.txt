HTML-dokument
Alla olika HTML-dokument ligger i templates. Alla filer �rver hela layouten fr�n layout.html via taggen
{% extends "layout.html" %}.
Varje sida �ndrar sedan endast inneh�llet i mitten av f�nstret.

I mitten p� layout.html s� finns f�ljande tags:

{% block homepage %}

och 

{% endblock %}


Det �r mellan dessa tag som de �rvande dokumenten "fyller i" med deras kontent genom att skriva tagsen:

{% block content %}

H�R EMELLAN �R HTML-KODEN F�R RESPEKTIVE HTML-DOKUMENT 

{% end block content %}






Hur man anv�nder funktioner i HTML-dokumenten:
Man kan skicka med parametrar n�r man renderar HTML-dokument fr�n routes.py. Dessa kan man hantera i HTML-dokumentet
genom att man skriva koden inne i f�ljande tags:

{{ kod h�r }}

F�r att b�rja en loop av n�got slag, exempelvis en for-loop:

{% for %}
{{ kod h�r }}
{% endfor %}