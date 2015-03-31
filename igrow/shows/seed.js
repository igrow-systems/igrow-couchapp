function(doc, req) {  

  var ddoc = this;
  var Mustache = require("lib/mustache");
  var path = require("vendor/couchapp/lib/path").init(req);

  var indexPath = path.list('index','recent-seeds',{descending:true, limit:10});
  var feedPath = path.list('index','recent-seeds',{descending:true, limit:10, format:"atom"});
  var commentsFeed = path.list('seeds','seeds',{descending:true, limit:10, format:"atom"});

  var data = {
    header : {
      index : indexPath,
      igrowName : ddoc.igrow.title,
      feedPath : feedPath,
      commentsFeed : commentsFeed
    },
    sidebar : {
      seedPath : path.show("seed")+"/",
      sowingPath : path.show("sowing")+"/",
      pottingPath : path.show("potting")+"/",
      labelsPath : path.list("labels")+"/"
    },
    scripts : {},
    pageTitle : doc ? "Edit: " + doc.common_name : "Create a new seed",
    assets : path.asset()
  };
  
  if (doc) {
    data.doc = JSON.stringify(doc);
 
    data.tags = doc.tags.join(", ");
    data.user = doc.user;
    data.created = doc.created;
    data.modified = doc.modified;
    data.binomial_name = doc.binomial_name;
    data.common_name = doc.common_name;
    data.variety_or_cultivar = doc.variety_or_cultivar;
    data.variety_url = doc.variety_url;
    data.supplier = doc.supplier;
    data.supplier_id = doc.supplier_id;
    data.pack_size = doc.pack_size;
    data.price = doc.price;
    data.type = doc.type; 
    
  } else {
    data.doc = JSON.stringify({
      type : "seed"
    });
  }

  return Mustache.to_html(ddoc.templates.editseed, data, ddoc.templates.partials);

}
