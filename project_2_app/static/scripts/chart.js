$(document).ready(function(){
    console.log("chart.js up and running")
});

// Chart One 
function drawChartOne() {

var data = google.visualization.arrayToDataTable(entitiesRows);

var options = {
    title: 'Correlation between life expectancy, fertility rate ' +
    'and population of some world countries (2010)',
    hAxis: {title: 'Life Expectancy'},
    vAxis: {title: 'Fertility Rate'},
    bubble: {textStyle: {fontSize: 11}}
};

var chart = new google.visualization.BubbleChart(document.getElementById('series_chart_div'));
chart.draw(data, options);
}

// Chart Two
function drawChartTwo() {

var data = google.visualization.arrayToDataTable(emotionRow);

var options = {
    width: 400, height: 120,
    redFrom: 90, redTo: 100,
    yellowFrom:75, yellowTo: 90,
    minorTicks: 5
};

var chart = new google.visualization.Gauge(document.getElementById('chart_div'));

    chart.draw(data, options);

    setInterval(function() {
        data.setValue(0, 1, 40 + Math.round(60 * Math.random()));
        chart.draw(data, options);
    }, 13000);
    setInterval(function() {
        data.setValue(1, 1, 40 + Math.round(60 * Math.random()));
        chart.draw(data, options);
    }, 5000);
    setInterval(function() {
        data.setValue(2, 1, 60 + Math.round(20 * Math.random()));
        chart.draw(data, options);
}, 26000);
}

// Chart Three
function drawChartThree() {

var data = google.visualization.arrayToDataTable(emotionRowsBar);

var options = {
    title : 'Emotional Analysis of Likes',
    vAxis: {title: 'Percentage'},
    seriesType: 'bars',
    animation:{
        "startup": true,
        duration: 6000,
        easing: 'out',
    },
    };

var chart = new google.visualization.ComboChart(document.getElementById('chart_div_emotion'));
    chart.draw(data, options);
}
// Chart Four
function drawChartFour() {

var data = google.visualization.arrayToDataTable(keywordsRows);

var options = {
    title: 'Keyword correlation Between Joy & Anger ',
    hAxis: {title: 'Joy'},
    vAxis: {title: 'Anger',
    direction: -1
    },
    bubble: {textStyle: {fontSize: 11}},
    animation:{
        "startup": true,
        duration: 6000,
        easing: 'inAndOut',
    },
};

var chart = new google.visualization.BubbleChart(document.getElementById('series_chart_div_key'));
    chart.draw(data, options);
}

// Chart Five
function drawChartFive() {

var data = google.visualization.arrayToDataTable(entitiesRows);

var options = {
    title: 'Entity correlation Between Joy & Sadness ',
    hAxis: {title: 'Joy'},
    vAxis: {title: 'Sadness',
            direction: -1
    },
    bubble: {textStyle: {fontSize: 11}},
    animation:{
        "startup": true,
        duration: 6000,
        easing: 'out',
    },
};

var chart = new google.visualization.BubbleChart(document.getElementById('series_chart_div_entities'));
    chart.draw(data, options);
}

// Chart Six
function drawChartSix() {

var data = google.visualization.arrayToDataTable(entitiesRowsBar);

var options = {
    title : 'Top 10 Most Relevant Entities by Emotion and Score',
    vAxis: {title: 'Emotion Score'},
    hAxis: {title: 'Entity/Keyword'},
    seriesType: 'bars',
    series: {1: {type: 'line'}},
    animation:{
        "startup": true,
        duration: 6000,
        easing: 'out',
    },
    };
    var chart = new google.visualization.ComboChart(document.getElementById('chart_div_entities'));
    chart.draw(data, options);
}

// Chart Seven
function drawChartSeven() {

var data = google.visualization.arrayToDataTable(keywordsRowsBar);

var options = {
    title : 'Top 10 Most Relevant Entities by Emotion and Score',
    vAxis: {title: 'Emotion Score'},
    hAxis: {title: 'Entity/Keyword'},
    seriesType: 'bars',
    series: {3: {type: 'line'}},
    
    animation:{
        "startup": true,
        duration: 6000,
        easing: 'in',
    },
    };
    var chart = new google.visualization.ComboChart(document.getElementById('chart_div_key'));
    chart.draw(data, options);
}

// arrays and variables for google charts
var p = 100
var endpoint = '/user/api/'
var entitiesRows = [['ID', 'Joy', 'Sadness', 'Fear', 'Anger', 'Disgust']]
var entitiesRowsBar = [['ID', 'Joy', 'Sadness', 'Fear', 'Anger', 'Disgust']]
var keywordsRows = [['ID', 'Joy', 'Anger', 'Sadness', 'Anger', 'Fear', 'Disgust']]
var keywordsRowsBar = [['ID', 'Joy', 'Anger', 'Sadness', 'Anger', 'Fear', 'Disgust']]
var emotionRow = [['Label', 'Value']]
var emotionRowsBar = [['ID','Joy', 'Anger', 'Sadness', 'Fear', 'Disgust', 'Sentiment']]
var categoriesRows = [['ID', 'Categories', 'Confidence Score' ]]
var categoriesRowsBar = [['ID', 'Categories', 'Confidence Score' ]]

$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
        console.log(data)
    
    // build arrays for chartOne, chartFive and chartSix
    for (var i=1; i<data.entities.length; i++){
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

    // build arrays for chartFour and chartSeven
    for (var i=1; i<data.keywords.length; i++){
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
    } else
    keywordsRows.push(keywordsRow)
    }
    // build array for chartTwo
    emotionRow.push(['Joy',data.emotion.document.emotion.joy *p])
    emotionRow.push(['Anger',data.emotion.document.emotion.anger * p])
    emotionRow.push(['Sadness',data.emotion.document.emotion.sadness * p])
    emotionRow.push(['Fear',data.emotion.document.emotion.fear * p])
    emotionRow.push(['Disgust',data.emotion.document.emotion.disgust * p])
    
    // build array for chartThree
    emotionRowsBar.push(["", 
    data.emotion.document.emotion.joy *p,
    data.emotion.document.emotion.anger * p,
    data.emotion.document.emotion.sadness * p,
    data.emotion.document.emotion.fear * p,
    data.emotion.document.emotion.disgust * p,
    data.sentiment.document.score *p])
    
    // build arrays for chartEight and chartNine
    for (let i=1; i<data.categories.length; i++){
    var categoriesRow = []
    
    categoriesRow.push(data.categories[i].label)
    categoriesRow.push(data.categories[i].score * p)
    if(i<10){
    categoriesRows.push(categoriesRow)
    categoriesRowsBar.push(categoriesRow)
    } else
    categoriesRows.push(categoriesRow)
    }

    // console log all arrays
    console.log(entitiesRows)
    console.log(entitiesRowsBar)
    console.log(keywordsRows)
    console.log(keywordsRowsBar)
    console.log(emotionRow)
    console.log(emotionRowsBar)
    console.log(categoriesRows)
    console.log(categoriesRowsBar)

    // chart 1
    google.charts.setOnLoadCallback(drawChartOne);
    // chart 2
    google.charts.setOnLoadCallback(drawChartTwo);
    // chart 3
    google.charts.setOnLoadCallback(drawChartThree);
    // chart 4
    google.charts.setOnLoadCallback(drawChartFour);
    // chart 5
    google.charts.setOnLoadCallback(drawChartFive);
    // chart 6
    google.charts.setOnLoadCallback(drawChartSix);
    // chart 7
    google.charts.setOnLoadCallback(drawChartSeven);
    },
    error: function(error_data){
        console.log("error")
        console.log(error_data)
    }
});
