{%include "javascript/corkscrew_base.js"%}

function move_file_to_dir(f,d){
    console.debug("moving "+f+" to "+d);
    post_and_redirect('/move_file', {file:f, dir:d});
}


function bookmark_this_page(){
    var this_url = '/' + location.href.replace(/^(?:\/\/|[^\/]+)*\//, "");
    var answer = confirm("bookmark this url? " + this_url);
    if (answer){
        post_and_redirect(
            '/_settings/add/',
            {name:'bookmark_'+name, back:this_url, value:this_url});
    }
}

function show_modal(){
    $('#basic-modal-content').modal();
}
