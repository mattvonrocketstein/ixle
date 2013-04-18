function(doc){
    if( !doc.{{fieldname}} ){
        emit(doc.id, doc)
    }
}