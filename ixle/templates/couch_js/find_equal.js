function(doc){
    var js_fval = '{{value}}';
    if(js_fval=='True'){
        js_fval = true;
    }
    if( doc['{{fieldname}}']==js_fval ){
        emit(doc._id, doc)
    }
}