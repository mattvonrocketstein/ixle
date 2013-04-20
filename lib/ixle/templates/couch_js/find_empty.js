function(doc){
    if( !doc.{{fieldname}} ){
        emit(doc._id, doc)
    }
}