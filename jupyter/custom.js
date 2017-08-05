var jq = document.createElement('script');
jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js";
document.getElementsByTagName('head')[0].appendChild(jq);
// ... give time for script to load, then type (or see below for non wait option)
jQuery.noConflict();

let $nt  = $("#notebook");
var t = $("<div>", {id: 'foo'});
$nt.append(t);


$nt.css("display", "flex")

var alloutput = $(".output_wrapper");
for (let i=0; i< alloutput.length; i++)
  t.append(alloutput[i])



height: 100px
overflow: scroll

感觉差不多了

然后呢 右边highlight感觉不容易做





  define([
      'notebook/js/outputarea'
  ], function(outputarea) {
    console.log('outputarea', outputarea)
  });
