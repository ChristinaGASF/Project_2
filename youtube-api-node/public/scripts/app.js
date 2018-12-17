console.log('in-sanity check');

var youtubeBaseURL= 'https://youtube.com/watch?v=';
var part= 'snippet', regionCode='US', chart='mostPopular';
var maxResults= 10;
var i= 0, maxResults= 20;
var key= '{YOUR_API_KEY}';
var baseURL= `https://www.googleapis.com/youtube/v3/search?part=${part}&regionCode=${regionCode}&maxResults=${maxResults}&key=${key}`;
var trendingURL= `${baseURL}&chart=${chart}`;

var trendings;


function populatePage(json) {
    var items= json.items;
    items.forEach((item)=>{
        if (trendings.length>=maxResults) return;
        trendings.push(item);
        i++;
        var vid= item.id.videoId;
        var snippet= item.snippet;
        var thumbnails= snippet.thumbnails.medium;
        $('#show').append(`
          <article>
            <h3>${i} -> ${snippet.title}</h3>
            <a href='${youtubeBaseURL}${vid}' target='_blank'>
              <img src='${thumbnails.url}' alt='${vid}' style='width:${thumbnails.width};height:${thumbnails.height};'>
            </a>
            <p>Uploaded at ${snippet.publishedAt}</p>
          </article>
        `);
    });
}

function ajaxCallMostPopular(nextPage) {
    var url= `${trendingURL}&order=viewCount`;
    if (nextPage!='') {
        url= `${trendingURL}&pageToken=${nextPage}`;
    } 
    $.ajax({
        method: 'GET',
        url: url,
        success: function(json) {
            var nextpage= json.nextPageToken;
            populatePage(json);
            if (trendings.length<maxResults) ajaxCallQuery(nextpage);
        },
        error: function(e1,e2,e3) { console.log('e1:',e1,', e2:',e2,', e3:',e3); }
    });
}


function ajaxCallQuery(keyword,nextPage) {
    if (!(/\S/.test(keyword))) return;
    var url= `${baseURL}&q=${keyword}&order=relevance`;
    console.log(keyword.replace(/\s/g,'+'));
    if (nextPage!='') {
        url= `${requestURL}&pageToken=${nextPage}`;
    }
    $.ajax({
        method: 'GET',
        url: url,
        success: function(json) {
            var nextpage= json.nextPageToken;
            populatePage(json);
            if (trendings.length<maxResults) ajaxCallMostPopular(nextpage);
        },
        error: function(e1,e2,e3) { console.log('e1:',e1,', e2:',e2,', e3:',e3); }
    });
}

function clear() {
    $('#show').html('');
    trendings= [];
    i= 0;
}

$(document).ready(function(){

    $('#btn_trending').on('click',function(){
        clear();
        ajaxCallMostPopular('');
    });

    $('#btn_query').on('click',function(){
        var keywords= $('#input_query').val();
        if (keywords=='') return;
        clear();
        ajaxCallQuery(keywords,'');
    });

});
