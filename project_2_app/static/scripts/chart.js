var p = 100
var endpoint = '/user/api/'
var entitiesRows = [['ID', 'Joy', 'Sadness', 'Fear', 'Anger', 'Disgust']]
var entitiesRowsBar = [['ID', 'Joy', 'Sadness', 'Fear', 'Anger', 'Disgust']]
var keywordsRows = [['ID', 'Joy', 'Anger', 'Sadness', 'Anger', 'Fear', 'Disgust']]
var keywordsRowsBar = [['ID', 'Joy', 'Anger', 'Sadness', 'Anger', 'Fear', 'Disgust']]
var emotionRow = [['Label', 'Value']]

$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
        console.log(data)
        console.log(data.customers)
        $('.append').append(data.customers)
        
    for (let i=1; i<data.entities.length; i++){
    var entitiesRow = []

    entitiesRow.push(data.entities[i].text)
    entitiesRow.push(data.entities[i].emotion.joy * p)
    entitiesRow.push(data.entities[i].emotion.sadness * p)
    entitiesRow.push(data.entities[i].emotion.fear * p)
    entitiesRow.push(data.entities[i].emotion.anger * p)
    entitiesRow.push(data.entities[i].emotion.disgust * p)
    if(i<10){
    entitiesRows.push(entitiesRow)
    entitiesRowsBar.push(entitiesRow)
    } else
    entitiesRows.push(entitiesRow)
    }
    console.log(entitiesRow)
    console.log(entitiesRows)
    console.log(entitiesRowsBar)

    for (let i=1; i<data.keywords.length; i++){
    var keywordsRow = []
    
    keywordsRow.push(data.keywords[i].text)
    keywordsRow.push(data.keywords[i].emotion.joy * p)
    keywordsRow.push(data.keywords[i].emotion.anger * p)
    keywordsRow.push(data.keywords[i].emotion.sadness * p)
    keywordsRow.push(data.keywords[i].emotion.anger * p)
    keywordsRow.push(data.keywords[i].emotion.fear * p)
    keywordsRow.push(data.keywords[i].emotion.disgust * p)
    if(i<10){
    keywordsRows.push(keywordsRow)
    keywordsRowsBar.push(keywordsRow)
    }
    keywordsRows.push(keywordsRow)
    }
    console.log(keywordsRow)
    console.log(keywordsRows)
    console.log(keywordsRowsBar)

    emotionRow.push(['Joy',data.emotion.document.emotion.joy *p])
    emotionRow.push(['Anger',data.emotion.document.emotion.anger * p])
    emotionRow.push(['Sadness',data.emotion.document.emotion.sadness * p])
    emotionRow.push(['Fear',data.emotion.document.emotion.fear * p])
    emotionRow.push(['Disgust',data.emotion.document.emotion.disgust * p])
    
    console.log(emotionRow)
    },
    error: function(error_data){
        console.log("error")
        console.log(error_data)
    }
})