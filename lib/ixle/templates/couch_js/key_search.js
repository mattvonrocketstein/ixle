function(doc){
    if (doc._id.indexOf('{{substring}}') != -1) {
        emit(doc.id, doc)
    }
}
