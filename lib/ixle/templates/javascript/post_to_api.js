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
function done_posting_to_api(data){
    console.debug('raw api result:');
    console.debug(data);
    var data = eval(data);
    console.debug('interpretted api result:')
    console.debug(data);
    var ppTable = prettyPrint(data);
    $('#block_body').html('' + $(ppTable).html());
    if(data['error']){
        flash('ERROR: ' + data['error'])}
    else if(data['last_error']){
        console.debug('maybe good');
        console.debug(data);}
    else{
        console.debug('looks good')
        console.debug(data);
    }
    //if(data.redirect_to){
    //window.location=data.redirect_to}
}
function post_to_api(api_name){
    flash('posting to api@' + api_name);
    var answer = confirm("post \"{{_}}\" to api @ " + api_name)
    if (answer){
        $.ajax({type : 'GET',
                url : '/api',
                data :  { 'cache' : (new Date()).getTime()+'',
                          'action' : api_name,
                          '_' : {{_|escapejs}}}})
            .success(done_posting_to_api)
            .fail(function(data){
                console.debug(data);
                flash('ERROR: ' + data)});
    }
    else{
        flash("canceled posting to api");
    }
}
