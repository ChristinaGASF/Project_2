$(document).ready(function(){
    console.log("jQuery up and running")
});


curl -X GET -u "apikey":"hB8gmTcFeu7MNsKDbRhW8_AYWntJn0sTcEV8A6SGJA7c" \ 
  "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2018-11-16&url=www.ibm.com&features=keywords,entities&entities.emotion=true&entities.sentiment=true&keywords.emotion=true&keywords.sentiment=true"