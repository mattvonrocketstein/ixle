//finds documents under
function(doc){
    if (doc._id.substring(0, '{{substring}}'.length) === '{{substring}}'){
        if( doc['{{fieldname}}']=={{value}} ){
            emit(doc.id, doc)
        }
    }
}
