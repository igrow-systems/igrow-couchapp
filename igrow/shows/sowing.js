function(doc, req) {

	  var ddoc = this;
	  var Mustache = require("lib/mustache");
	  var List = require("vendor/couchapp/lib/list");
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
	    pageTitle : doc ? "Edit: " + doc.modified + " - " + doc.seed.common_name + ", " + doc.seed.variety_or_cultivar : "Create a new sowing",
	    assets : path.asset()
	  };
	  
	  if (doc) {
	    data.doc = JSON.stringify(doc);
	 
	    data.tags = doc.tags.join(", ");
	    data.user = doc.user;
	    data.created = doc.created;
	    data.modified = doc.modified;

	    data.quantity = doc.quantity;
	    data.type = doc.type; 
	    
	  } else {
	    data.doc = JSON.stringify({
	      type : "sowing"
	    });
	    
	    /*data.seeds = List.withRows(function(row) {
	      log(row);
          var v = row.value;
          if (v.type != "seed") {
            return;
          }
          // keep getting
          return {
            seed : {
              id                  : v._id,
              common_name         : v.common_name,
              variety_url         : v.variety_url,
              variety_or_cultivar : v.variety_or_cultivar,
              supplier            : v.supplier,
              created             : v.created
            }
          };
        });*/
	  }
	  log(data);

	  var html = Mustache.to_html(ddoc.templates.editsowing, data, ddoc.templates.partials);
	  log(html);
	  return html;

}