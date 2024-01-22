// Frontend application for the Tawny project
// Uses ArangoDB backend

var express = require('express');
var arangojs = require('arangojs');

var app = express();
app.set('view engine', 'ejs');

app.get('/', function (req, res) {
  //get arangourl from secrets.json
  let arangoUrl = "https://" + require('./secrets.json').arangoUsername + ':' + require('./secrets.json').arangoPassword + '@' + require('./secrets.json').arangoHost;

  var db = new arangojs.Database(arangoUrl);

  var arangoResults;

  //aql query to get 20 random organizations
  var aqlQuery = 
  `
  FOR org IN Organizations
    RETURN org
  `
  db.database("Tawny").query(aqlQuery).then(cursor => cursor.all()
  ).then(results => {
    //store data in var arangoResults
    arangoResults = results;
    
    res.render("index", {arangoResults: arangoResults});
  });
});

app.listen(8080, function () {
  console.log('Example app listening on port 8080!');
});