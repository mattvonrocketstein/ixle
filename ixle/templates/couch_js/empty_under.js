 function(doc){
    if (doc._id.substring(0, '{{substring}}'.length) === '{{substring}}'){
        if ( !doc.{{fieldname}} ){
            emit(doc.id, doc)
        }
    }
}