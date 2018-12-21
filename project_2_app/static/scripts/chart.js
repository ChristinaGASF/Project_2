
$(window).resize(function() {
    if(this.resizeTO) clearTimeout(this.resizeTO);
    this.resizeTO = setTimeout(function() {
        $(this).trigger('resizeEnd');
    }, 500);
});
$(window).on('resizeEnd',function(){

    drawChartTwo(drawChartTwo);
    // // chart 3
    drawChartThree(drawChartThree);
    // // chart 3.5
    drawChartThreeFive(drawChartThreeFive);
    // chart 4
    drawChartFour(drawChartFour);
    // // chart 5
    drawChartFive(drawChartFive);
    // // chart 6
    drawChartSix(drawChartSix);
    // // chart 7
    drawChartSeven(drawChartSeven);
});

$(document).ready(function(){
    console.log("chart.js up and running")
});

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
        title : 'Emotional Analysis of Liked Videos',
        vAxis: {title: 'Percentage'},
        seriesType: 'bars',
        animation:{
            "startup": true,duration: 6000,easing: 'out',
        },
    };

    var chart = new google.visualization.ComboChart(document.getElementById('chart_div_emotion'));
    chart.draw(data, options);
}

function drawChartThreeFive() {

    var data = google.visualization.arrayToDataTable(categoriesRows);
    
    var options = {
        title : 'Main Categories of Liked Videos',
        vAxis: {title: 'Confidence score for category classification'},
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
        title: 'Keyword Correlation Between Joy & Anger ',
        hAxis: {title: 'Likeliness to Convey: Joy'},
        vAxis: {title: 'Likeliness to Convey: Anger',direction: -1},
        bubble: {textStyle: {fontSize: 11}},
        animation:{
            "startup": true,duration: 6000,easing: 'inAndOut',
        },
    };

    var chart = new google.visualization.BubbleChart(document.getElementById('series_chart_div_key'));
    chart.draw(data, options);
}

// Chart Five
function drawChartFive() {

    var data = google.visualization.arrayToDataTable(entitiesRows);

    var options = {
        title: 'Entity Correlation Between Joy & Sadness ',
        hAxis: {title: 'Likeliness to Convey: Joy'},
        vAxis: {title: 'Likeliness to Convey: Sadness',direction: -1},
        bubble: {textStyle: {fontSize: 11}},
        animation:{
            "startup": true,duration: 6000,easing: 'out',
        },
    };

    var chart = new google.visualization.BubbleChart(document.getElementById('series_chart_div_entities'));
    chart.draw(data, options);
}

// Chart Six
function drawChartSix() {

var data = google.visualization.arrayToDataTable(entitiesRowsBar);

    var options = {
        title : 'Likeliness to Convey: Each Emotion',
        vAxis: {title: 'Likeliness to Convey: Each Emotion'},
        hAxis: {title: 'Entity'},
        seriesType: 'bars',
        series: {1: {type: 'line'}},
        animation:{
            "startup": true,duration: 6000,easing: 'out',
        },
    };
    var chart = new google.visualization.ComboChart(document.getElementById('chart_div_entities'));
    chart.draw(data, options);
}

// Chart Seven
function drawChartSeven() {

    var data = google.visualization.arrayToDataTable(keywordsRowsBar);

    var options = {
        title : 'Top Keywords by Emotion and Score',
        vAxis: {title: 'Likeliness to Convey: Each Emotion'},
        hAxis: {title: 'Keyword'},
        seriesType: 'bars',
        series: {3: {type: 'line'}},
        animation:{
            "startup": true,duration: 6000,easing: 'in',
        },
    };
    var chart = new google.visualization.ComboChart(document.getElementById('chart_div_key'));
    chart.draw(data, options);
}

var data= $('textarea').html().trim();

// arrays and variables for google charts
var p = 100;
var entitiesRows = [['ID', 'Joy', 'Sadness', 'Fear', 'Anger', 'Disgust']]
var entitiesRowsBar = [['ID', 'Joy', 'Sadness', 'Fear', 'Anger', 'Disgust']]
var keywordsRows = [['ID', 'Joy', 'Anger', 'Sadness', 'Anger', 'Fear', 'Disgust']]
var keywordsRowsBar = [['ID', 'Joy', 'Anger', 'Sadness', 'Anger', 'Fear', 'Disgust']]
var emotionRow = [['Label', 'Value']]
var emotionRowsBar = [['ID','Joy', 'Anger', 'Sadness', 'Fear', 'Disgust', 'Senitment']]
var categoriesRows = [['Categories', 'Confidence Score' ]]
var categoriesRowsBar = [['Categories', 'Confidence Score' ]]



if (data=='') {
    $('textarea').attr('style','display:block;');
    $('textarea').html('No Videos saved...');
    window.location.href='/profile/';
} else {

    data= JSON.parse(data);

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
        emotionRow.push(['Sentiment',data.sentiment.document.score *p])
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
        for (let i=0; i<data.categories.length; i++){
        var categoriesRow = []
        
        categoriesRow.push(data.categories[i].label,data.categories[i].score * p)
        if(i<10){
        categoriesRows.push(categoriesRow)
        categoriesRowsBar.push(categoriesRow)
        } else
        categoriesRows.push(categoriesRow)
    }

    // chart 2
    google.charts.setOnLoadCallback(drawChartTwo);
    // chart 3
    google.charts.setOnLoadCallback(drawChartThree);
    // chart 3-5
    google.charts.setOnLoadCallback(drawChartThreeFive);
    // chart 4
    google.charts.setOnLoadCallback(drawChartFour);
    // chart 5
    google.charts.setOnLoadCallback(drawChartFive);
    // chart 6
    google.charts.setOnLoadCallback(drawChartSix);
    // chart 7
    google.charts.setOnLoadCallback(drawChartSeven);
}
