console.log('in-sanity check');

var youtubeBaseURL= 'https://youtube.com/watch?v=';
var part= 'snippet,contentDetails,statistics', regionCode='US', chart='mostPopular';
var order= 'viewCount';
var maxResults= 10;
var i= 0, maxShowResults= 20;
var key= 'REPLACE_API';
var baseURL= `https://www.googleapis.com/youtube/v3/videos?part=${part}&regionCode=${regionCode}&maxResults=${maxResults}&order=${order}&key=${key}`;
var trendingURL= `${baseURL}&chart=${chart}`;

var trendings;
var youtube_cats= [];


function populatePage(json) {
    var items= json.items;
    items.forEach((item)=>{
        if (trendings.length>maxShowResults) return;
        trendings.push(item);
        i++;
        var vid= item.id;
        var snippet= item.snippet;
        var thumbnails= snippet.thumbnails.medium;
        var tags= snippet.tags!==undefined? snippet.tags.join(', ') : 'no tags';
        $('#show').append(`
          <article>
            <h3>${i} -> ${snippet.title}</h3>
            <h5>Cat_id= ${snippet.categoryId}</h5>
            <h4>Channel Title: ${snippet.channelTitle}</h4>
            <a href='${youtubeBaseURL}${vid}' target='_blank'>
              <img src='${thumbnails.url}' alt='${vid}' style='width:${thumbnails.width};height:${thumbnails.height};'>
            </a>
            <p>Uploaded at ${snippet.publishedAt}</p>
            <p>${tags}</p>
          </article>
        `);
    });
}

function ajaxCallMostPopular(nextPage) {
    var url= trendingURL;
    if (nextPage!='') {
        url= `${trendingURL}&pageToken=${nextPage}`;
    } 
    $.ajax({
        method: 'GET',
        url: url,
        success: function(json) {
            var nextpage= json.nextPageToken;
            console.log(json);
            populatePage(json);
            if (trendings.length<maxShowResults) ajaxCallMostPopular(nextpage);
        },
        error: function(e1,e2,e3) { console.log('e1:',e1,', e2:',e2,', e3:',e3); }
    });
}


function ajaxCallQuery(cat_id,nextPage) {
    var url= `${trendingURL}&videoCategoryId=${cat_id}`;
    if (nextPage!='') {
        url= `${url}&pageToken=${nextPage}`;
    }
    $.ajax({
        method: 'GET',
        url: url,
        success: function(json) {
            var nextpage= json.nextPageToken;
            console.log(json);
            populatePage(json);
            if (trendings.length<maxShowResults) ajaxCallQuery(cat_id,nextpage);
        },
        error: function(e1,e2,e3) { console.log('e1:',e1,', e2:',e2,', e3:',e3); }
    });
}

function clear() {
    $('#show').html('');
    trendings= [];
    i= 0;
}

function populateCategories() {
    youtube_categories_json.items.forEach((item)=>{
        youtube_cats.push({
            'id': item.id,
            'title': item.snippet.title,
        });
        $('#select_cat').append(`
          <option value='${item.id}'>${item.snippet.title}</option>
        `);
    });
    $('#select_cat').children().eq(0).attr('selected','selected');
}

$(document).ready(function(){

    populateCategories();    

    ///*
    $('#btn_trending').on('click',function(){
        clear();
        ajaxCallMostPopular('');
    });

    $('#btn_query').on('click',function(){
        var cat_id= $('#select_cat option:selected').val();
        //console.log(cat_id); return;
        if (cat_id=='') return;
        clear();
        ajaxCallQuery(cat_id,'');
    });
    //*/
});
