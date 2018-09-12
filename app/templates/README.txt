HTML-dokument
Alla olika HTML-dokument ligger i templates. Alla filer ärver hela layouten från layout.html via taggen
{% extends "layout.html" %}.
Varje sida ändrar sedan endast innehållet i mitten av fönstret.

I mitten på layout.html så finns följande tags:

{% block homepage %}

och 

{% endblock %}


Det är mellan dessa tag som de ärvande dokumenten "fyller i" med deras kontent genom att skriva tagsen:

{% block content %}

HÄR EMELLAN ÄR HTML-KODEN FÖR RESPEKTIVE HTML-DOKUMENT 

{% end block content %}






Hur man använder funktioner i HTML-dokumenten:
Man kan skicka med parametrar när man renderar HTML-dokument från routes.py. Dessa kan man hantera i HTML-dokumentet
genom att man skriva koden inne i följande tags:

{{ kod här }}

För att börja en loop av något slag, exempelvis en for-loop:

{% for %}
{{ kod här }}
{% endfor %}