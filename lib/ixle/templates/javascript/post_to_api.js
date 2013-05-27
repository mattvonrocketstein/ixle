//
function flash(msg){
    if( $('.flashes') ){
        var _id = 'flash_' + Math.floor(Math.random()*200);
        $('.flashes').append('<li id=' + _id + '>'+msg+'</li>');
        var x = $('#'+_id);
        var delay = 10000;
        x.fadeOut(delay);
        setTimeout(function() { x.remove() }, delay);

    }
    else{
        alert(msg);}
}

function post_to_api(api_name){
    flash('posting to api@' + api_name);
    var answer = confirm("post \"{{_}}\" to api @ " + api_name)
    if (answer){
        $.ajax({type : 'GET',
                url : '/api',
                data :  { 'cache' : (new Date()).getTime()+'',
                          'action' : api_name,
                          '_' : '{{_}}'}})
            .done(function(data){flash('API-RESULTS:' + data)})
            .fail(function(data){flash('ERROR: ' + data)});
    }
    else{
        flash("canceled posting to api");
    }
}
