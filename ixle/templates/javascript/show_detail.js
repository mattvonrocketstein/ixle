function show_detail(_id){
    console.debug('showing detail for: ' + _id)
    var url = '/detail?_='+encodeURIComponent(_id);
    console.debug('translated to url: ' + url)
    window.location = url;
}