function(doc){
    if( doc['file_type']=='video' ){
        {% if path%}
        if(doc._id.substring(0,'{{path}}'.length)==='{{path}}'){
            {%endif%}
            emit(doc._id, doc)
            {% if path%}
        }{%endif%}

    }
}