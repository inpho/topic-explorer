var taTimeout;
$(".typeahead").typeahead({items: 12,
  source: function(query, process) {
    if (taTimeout)
      clearTimeout(taTimeout);

    this.$menu.find('.active').removeClass('active');
    taTimeout = setTimeout(function () {
      $.getJSON('docs.json?q=' + encodeURIComponent(query), function(data) {
        labels = [];
        mapped = {};
        $.each(data, function(i, item) {
          mapped[item.label] = item;
          labels.push(item.label);
        });
      
        process(labels);
    })}, 300);
  },
  updater: function(item) {
      if (!item) { 
        $('#hidden_id').val('');
        return this.$element.val();
      } else {
        $('#hidden_id').val(mapped[item].id);
        resetBars();
        return item;
      }
  },
  sorter: function(items) {
      /*if (items.length == 1) {
        $('#hidden_id').val(mapped[items[0]].id);
        console.log("setting hidden_id" + $('#hidden_id').val());
        if (!$('#autocompleteDoc').hasClass('active')) {
          $('#autocompleteDoc').addClass('active');
          $('span.icon-font', '#autocompleteDoc').removeClass('icon-font').addClass('icon-file');
        }
        items.length = 0;
      } else*/
      var query = this.query;
      items = items.sort();
      var start = items.filter(function(item) { return item.lastIndexOf(query, 0) == 0;});
      var elsewhere = items.filter(function(item) { return item.lastIndexOf(query, 0) != 0;});
      return start.concat(elsewhere);
  }
});

$('#randomDoc', '#fingerprintModal').click(function() { 
    $.getJSON(fingerprint.host + 'docs.json?random=1', function(rand) {
      $('#hidden_id', '#fingerprintModal').val(rand[0].id);
      $('#doc', '#fingerprintModal').val(rand[0].label);
      resetBars();
  });
});
$('#randomDoc', '#fingerprintModal').tooltip({title: "Random Document", placement: 'bottom'});

function resetBars() {
  $('#singleBarsDl').html('');
  $('#loading').show();
  $(ks).each(resetBar);
}

function resetBar(i, k) {
  var base_bar =
  '<dd class="bar-container" id="bar'+k+'">' 
  + '<div id="status" style="width:100%">'
  + '<div class="progress loading progress-striped active">'
  + '<div class="bar" style="width:25%">Loading documents...</div>'
  + '</div>'
  + '</div>'
  + '<div id="chart"> </div>'
  + '</dd>';
  
  $('#fingerprintModal #topicBars dl').append(base_bar);
  fingerprint.visualize(k);
  
}

function showFingerprint(id, label) {
  $('#doc', '#fingerprintModal').val(label);
  $('#hidden_id', '#fingerprintModal').val(id);
  $('#fingerprintModal').modal('show');
  $('#fingerprintModal').on('shown.bs.modal', 
    function(e) {
    if (!$('dd', '#singleBarsDl').length)
      resetBars()
    });
}
var fingerprint = {
  'host' : '',
  'visualize' : function(k) {
    
    var maxRows = 25;
    var minCols = 2;
    
    //${c.entity.sep_dir}
    var docid = $('#fingerprintModal #hidden_id').val();
    if (!docid || docid == '')
      return;
    
    var width = $('#fingerprintModal .bar-container').width(),
        height = 20;
    
    var x = d3.scale.linear()
        .range([0, width])
        .domain([0,1.0]);
     // TODO: Clear existing #bar{k} content
    var svg = d3.select("#bar"+k+" #chart").insert("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("id","main")
        .attr("class", "main");
    $('#bar'+k).hide();
    
    function calculateTopicMap(data, scale, sortFn){
      data.forEach(function(d) {
        var sizeFactor = (scale) ? d.prob : 1.0
        var x0 = 0;
        if (sortFn) d.topicMap =  d3.keys(d.topics)
          .sort(sortFn)
          .map(function(name) { return {name: name, x0: x0, x1: x0 += +(d.topics[name]*sizeFactor) }; });
        else d.topicMap = d3.keys(d.topics)
          .map(function(name) { return {name: name, x0: x0, x1: x0 += +(d.topics[name]*sizeFactor) }; });
      });
      
    }
    
    var url = "/docs_topics/" + $('#fingerprintModal #hidden_id').val() + '.json?n=1'
    var host = fingerprint.host + k;
    
    d3.json(host + url, function(error, data) {
      $('#fingerprintModal #status .bar', '#bar'+k).css('width', '50%').text('Loading topics...');
      if (error) {
        var isError = $('.bar.bar-danger ');
        $('#fingerprintModal #status .progress', '#bar'+k).removeClass('active progress-striped');
        if(isError[0]){
           $('#fingerprintModal #status .progress', '#bar'+k).remove();
        }
        else{
          var errormsg = "Invalid document: " + docid + ".";
          $('#fingerprintModal #status .bar', '#bar'+k).addClass('bar-danger').text(errormsg);
        }
        return false;
      }
      d3.json(host + "/topics.json", function(error_top, topics) {
        $('#fingerprintModal #status .bar', '#bar'+k).css('width', '75%').text('Rendering chart...');
        if (error_top) {
           var isError = $('.bar.bar-danger ');
          $('#fingerprintModal #status .progress', '#bar'+k).removeClass('active progress-striped');
          if(isError[0]){
             $('#fingerprintModal #status .progress', '#bar'+k).remove();
          }
          else{
          $('#fingerprintModal #status .bar', '#bar'+k).addClass('bar-danger').text('Could not load topic list.');
          }
          return false;
        }
    
        var k = d3.keys(topics).length;
        var full_explorer_url = host+"/?doc="+encodeURIComponent(docid);
      
        calculateTopicMap(data, true, function(a,b) {return data[0].topics[b] - data[0].topics[a];});
      
        // draw total bar
        var doc = svg.selectAll("doc")
            .data(data)
          .enter().append("g")
            .attr("class","doc");
      
        // Draw topic bars
        doc.selectAll("rect")
            .data(function(d) { return d.topicMap; })
          .enter().append("rect")
            .attr("height", height)
            .attr("x", function(d) { return x(d.x0); })
            .attr("width", function(d) { return x(d.x1) - x(d.x0); })
            .attr("class", function(d) { return "top_" + d.name; })
            .attr("title", function(d) { return d3.keys(topics[d.name]['words']).sort(function(a,b) {
                  if (topics[d.name]['words'][a] > topics[d.name]['words'][b])
                    return -1;
                  else if (topics[d.name]['words'][a] < topics[d.name]['words'][b])
                    return 1;
                  else
                    return 0;
                }).join(", ") + ", ..."; })
            .on("mouseover", function(d) {
                // SVG element z-index determined by render order, not style sheet
                // so element must be reappended to the end on hover so border 
                // is not occluded
                var parent = $(this).parent();
                $(this).detach().appendTo(parent);
              })
            .on("click", function(d) { window.location = full_explorer_url; })
            .style("fill", function(d) { return barColors(topics[d.name]['color'], d.name, svg); });
      
        $(".doc rect").tooltip({container:'body', 
                                animation: false, placement: 'top'});
        
        $('#status .bar', '#bar'+k).addClass('bar-success').css('width', '100%').text("Complete!");
        setTimeout(function() {$('#status', '#bar'+k).hide()}, 250);
        setTimeout(function() {
          $('#loading').hide();
          $('#bar'+k).show(); 
            $("#bar" + k).before("<dt>"+k+" Topics</dt>");
          }, 250);
    
    }); });
  } 
};





//splash.mustache.html
var converter = new showdown.Converter({
	simplifiedAutoLink: true,
	headerLevelStart : 3,
	literalMidWordUnderscores: true,
	strikethrough: true,
	tables: true
});

$.get('../description.md').
  done(function(data) { 
    var html = converter.makeHtml(data);
    $('#aboutText').html(html);
  }).fail(function(data) { $('#aboutText').html('To add a description of this corpus, create a Markdown file and edit the main:corpus_desc option in config.ini.');
});

var combineWords = function(words) {
  return d3.keys(words).sort(function(a,b) {
		if (words[a] > words[b])
			return -1;
		else if (words[a] < words[b])
			return 1;
		else
			return 0;
	}).join(", ") + ", ..."; 
}

var wordTimeout;
$('#words').on('input', function() {
  if (wordTimeout) clearTimeout(wordTimeout);
  var words = $(this).val().split(' ');
  wordTimeout = setTimeout(function() { 
    gettopics(words); 
    $('#wordsBtn').attr('href', 'topics?q=' + words.join('+'));
    $('#wordsBtn2').attr('href', 'topics?q=' + words.join('+'));
  }, 500);
});

var k_urls = ks.map(function(k) { return '../' + k + "/topics.json" });
var topics = Promise.all(k_urls.map($.getJSON)).then(function (data) {
	var t = {}; 
	data.forEach(function(d,i) {
		t[ks[i]] = $.each(d, function(key, val) { d[key] = combineWords(val.words) });
  });
  return t;
});

function gettopics(words) {
  var query = words.join('|');
  $('#wordsDl').html('')
  $.getJSON('topics.json?q=' + query)
  .error(function(error) {
  	console.log(error);
  	if (error.status == 404) {
      $('#words').parents('.form-group').addClass('has-error');
      $('#words').attr('placeholder', 'Terms not in corpus: "' + words + '". Try another query...');
      $('#words').val('');
    } else if (error.status == 410) { 
      $('#words').parents('.form-group').addClass('has-warning');
      $('#words').attr('placeholder', 'Terms removed by stoplisting: "' + words + '". Try another query...');
      $('#words').val('');
    }
  }).success(function(data) {
    $('#words').parents('.form-group').removeClass('has-error');
    $('#words').parents('.form-group').removeClass('has-warning');
    $('#words').parents('.form-group').addClass('has-success');
    Promise.resolve(topics).then(function(val) {
      for (var i = 0; i < 10; i++) {
        var k = data[i]['k'];
        var t = data[i]['t'];

	      /*$('#wordsDl').append('<dt><a href="' + k + '/?topic=' + t + '">' +
	        'Topic ' + t + 
	        ' <small>(k = ' + k + ')</small></a></dt>');
	      $('#wordsDl').append('<dd>' + 
	        val[k][t] + '</dd>'); }*/
	      $('#wordsDl').append('<div class="col-xs-4"><h4><a href="' + k + '/?topic=' + t + '">' +
	        'Topic ' + t +
	        ' <small>(k = ' + k + ')</small></a></h4><p>' +
	        val[k][t] + '</p></div>');
      }
      $('#wordsDl').append('<div class="clear">&nbsp;</div>');
    });
  });
}





//bars.mustache.html
//Handles cases where the "click a segment below to focus on relation to that topic" should appear or not.
//Also updates a newly added descriptor that indicates what sort of focus the application is in at the time,
//either topic focused or document focused.
var topDoc = document.getElementById("topicBtn");
var mainDoc = document.getElementById("doc");
$(window).load(function () {
	//Breaks out of function when there are no topic bars, like on the landing page
	if (topDoc == null) return;
  if (mainDoc.value == "") {
    if (roottopic == null) {
      $("#focalDoc").text("");
    } else {
      $("#focalDoc").text("Top 40 documents most similar to topic " + roottopic);
    }
    topDoc.style.display = 'none';
  }
  else {
    topDoc.style.display = 'block';
    if (roottopic == null) {
        $("#focalDoc").text("Top 40 documents most similar to the focal document");
    } else {
      $("#focalDoc").text("Top 40 documents most similar to topic " + roottopic);
    }
  }
});

$(document).ready(function () {
  $('#cite').hide();
  $('#citeBtn').tooltip({title: "Show citation info", placement: 'bottom'});

  var visited = document.cookie.replace(/(?:(?:^|.*;\s*)visited\s*\=\s*([^;]*).*$)|^.*$/, "$1");
  if (visited != null) {
    $('.help').hide();
    $('#helpBtn').tooltip({title: "Show help", placement: 'bottom'});
  }
  else {
    $('#helpBtn').tooltip({title: "Hide help", placement: 'bottom'});
    $('#helpBtn').addClass('active');
  }
  document.cookie = "visited=true; max-age=31536000;";
});
var scrollLegend;
$('#helpBtn').click(function() {
    $('.help').toggle();
    if (!$('#helpBtn').hasClass('active')) {
      $('#helpBtn').data('tooltip').options.title = "Hide help";
      $('#helpBtn').addClass('active');
    } else {
      $('#helpBtn').data('tooltip').options.title = "Show help";
      $('#helpBtn').removeClass('active');
    }
    scrollLegend();
  });
$('#citeBtn').click(function() {
    $('#cite').toggle();
    if (!$('#citeBtn').hasClass('active')) {
      $('#citeBtn').data('tooltip').options.title = "Hide citation info";
      $('#citeBtn').addClass('active');
    } else {
      $('#citeBtn').data('tooltip').options.title = "Show citation info";
      $('#citeBtn').removeClass('active');
    }
    scrollLegend();
  });

var q = inpho.util.getValueForURLParam('q') || null;
if (q) {
  q = decodeURIComponent(q);
  q = q.replace(/\|/g, ' ');
}

$('#doc').css('font-weight', 'bold');
$('#doc').on('change', function() { $(this).css('font-weight', 'normal')});

var docid = inpho.util.getValueForURLParam('doc') || null;
if (docid) {
  docid = decodeURIComponent(docid);
  $('#hidden_id').val(docid);
  $('.twitter-share-button').attr('data-text', "What's similar to " +docid+"? Discover with the #InPhO Topic Explorer");
  $.getJSON('../docs.json?id='+encodeURIComponent(docid), function(title) {
    if (title.length) {
      title = title[0].label;
      $('.title').html('{{doc_title_format}}'.format(title,'{{doc_url_format}}'.format(docid)));
      $('#doc').val(title);
      $('#autocompleteDoc').removeAttr('disabled').button('toggle');
      $('span.glyphicon-font', '#autocompleteDoc').removeClass('glyphicon-font').addClass('glyphicon-file');
      $('.twitter-share-button').attr('data-text', "What's similar to " + title +"? Discover with the #InPhO Topic Explorer!");
    } else {
      $('.title').html('{{doc_title_format}}'.format(docid,'{{doc_url_format}}'.format(docid)));
      $('#doc').val(docid);
    }
  });
} else if (q) {
    $('#search-label').html("Words")
    $('.title').html('the query "'+q+'"');
    $('#doc').val(q);  
/*  TODO: Migrate to call /docs.json?q=q
    title = data.filter(function(item) { return item.label.toLowerCase().indexOf(q.toLowerCase()) >= 0 });
    if (title.length) {
      $('#autocompleteDoc').removeAttr('disabled');
    }
    */

}
var roottopic = inpho.util.getValueForURLParam('topic') || null;

if (roottopic) {
  $('.title').html('Topic ' + roottopic);
  $('.twitter-share-button').attr('data-text', "Check out topic "+ roottopic+" at the #InPhO Topic Explorer!");
  $('.topdoc').text('Top Documents for Topic ' + roottopic);
  $('.topdoc').css('font-weight', 'bold');
  $('.topdoc').addClass('btn-default');
  $('.topdoc').removeClass('btn-primary');
  $('.topdoc').removeAttr('disabled');
}

if (docid || roottopic || q)
  $('.non-null').show()
else
  $('.null').show();

$('#searchForm').submit(function(event) {
  visualize(); 
  event.preventDefault();
});

function visualize(k) {
  var url = "{0}{1}".format(window.location.origin, window.location.pathname);
  if (k && tops)
    url = url.replace('/' + Object.keys(tops).length + '/',
                      '/' + k + '/');

  if ($("#autocompleteDoc").hasClass('active') && !($("#autocompleteDoc").attr("disabled") == 'disabled')) {
    url += "?doc=" + encodeURIComponent($("#hidden_id").val() || docid) ;
  } else {
    url += "?q=" + encodeURIComponent($("#doc").val()).replace(/%20/g, '|');
  }

  window.location = url;
}

var taTimeout;
$(".typeahead").typeahead({items: 12,
  source: function(query, process) {
    if (taTimeout)
      clearTimeout(taTimeout);

    this.$menu.find('.active').removeClass('active');
    taTimeout = setTimeout(function () {
      $.getJSON('../docs.json?q=' + encodeURIComponent(query), function(data) {
        labels = [];
        mapped = {};
        $.each(data, function(i, item) {
          mapped[item.label] = item;
          labels.push(item.label);
        });
      
        process(labels);
    })}, 300);
  },
  updater: function(item) {
      if (!item) { 
        if ($('#autocompleteDoc').hasClass('active')) {
          $('#autocompleteDoc').removeClass('active');
          $('span.glyphicon-file', '#autocompleteDoc').removeClass('glyphicon-file').addClass('glyphicon-font');
        }
        $('#hidden_id').val('');
        return this.$element.val();
      } else {
        if (!$('#autocompleteDoc').hasClass('active')) {
          $('#autocompleteDoc').addClass('active');
          $('span.glyphicon-font', '#autocompleteDoc').removeClass('glyphicon-font').addClass('glyphicon-file');
        }
        $('#autocompleteDoc').removeAttr('disabled');

        $('#hidden_id').val(mapped[item].id);
        return item;
      }
  },
  sorter: function(items) {
      /*if (items.length == 1) {
        $('#hidden_id').val(mapped[items[0]].id);
        console.log("setting hidden_id" + $('#hidden_id').val());
        if (!$('#autocompleteDoc').hasClass('active')) {
          $('#autocompleteDoc').addClass('active');
          $('span.glyphicon-font', '#autocompleteDoc').removeClass('glyphicon-font').addClass('glyphicon-file');
        }
        items.length = 0;
      } else*/
      if(items.length > 0) { 
        $('#autocompleteDoc').removeAttr('disabled');
      } else if (items.length == 0) {
        if ($('#autocompleteDoc').hasClass('active')) {
          $('#autocompleteDoc').removeClass('active');
          $('span.glyphicon-file', '#autocompleteDoc').removeClass('glyphicon-file').addClass('glyphicon-font');
        }
        $('#autocompleteDoc').attr('disabled','disabled');
      }
      var query = this.query;
      items = items.sort();
      var start = items.filter(function(item) { return item.lastIndexOf(query, 0) == 0;});
      var elsewhere = items.filter(function(item) { return item.lastIndexOf(query, 0) != 0;});
      return start.concat(elsewhere);
  }
});
  
$('#autocompleteDoc').click(function() {
  if (!$('#autocompleteDoc').hasClass('active'))
    $('.typeahead').typeahead('lookup').focus();
  else {
    $('#autocompleteDoc').removeClass('active');
    $('span.glyphicon-file', '#autocompleteDoc').removeClass('glyphicon-file').addClass('glyphicon-font');
    $('#hidden_id').val('');
  }
});


$('#randomDoc', '#searchForm').click(function() { 
    $.getJSON('../docs.json?random=1', function(rand) {
      if (!$('#autocompleteDoc').hasClass('active')) {
        $('#autocompleteDoc').button('toggle');
        $('span.glyphicon-font', '#autocompleteDoc').removeClass('glyphicon-font').addClass('glyphicon-file');
      }
      $('#autocompleteDoc').removeAttr('disabled');
      $('#hidden_id', '#searchForm').val(rand[0].id);
      $('#doc', '#searchForm').val(rand[0].label);
      $('#doc', '#searchForm').css('font-weight', 'normal');
      $('#submit', '#searchForm').removeClass('btn-default');
      $('#submit', '#searchForm').addClass('btn-primary');
  });
});
$('#randomDoc', '#searchForm').tooltip({title: "Random Document", placement: 'bottom'});









if ($('.scale')[0] != null) $('.scale')[0].checked = (roottopic != null); 

var ico;
var maxRows = 25;
var minCols = 2;

var margin = {top: 80, right: 40, bottom: 20, left: 15 + (icons.length * 20)},
    width = 960 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]);

var y = d3.scale.ordinal()
    .rangeRoundBands([0, height], .1, 0);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("top")
    .ticks(10, "%");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

function computeWidth(numCols) { 
  $('#legend').attr("width", margin.right + (numCols*55) + 20 + margin.right);
  $('#chart #main').attr("width", Math.max($(window).width() - $('#legend').width() - 200 + margin.right, 750));
  $('#controls').css("left", Math.max($(window).width() - $('#legend').width() - 200 + margin.right, 750) + 40);
  width = Math.max($(window).width() - $('#legend').width() - 200 + margin.right, 750) - margin.left - margin.right;
  x = d3.scale.linear()
    .range([0, width]);
  x.domain([0,1]);
  xAxis = d3.svg.axis()
    .scale(x)
    .orient("top")
    .ticks(10, "%");
}

// Changed the height variable to better pair the topic bars with their documents
function computeHeight(data, numLegendRows) { 
  height = (data.length * 35);// - margin.top - margin.bottom;
  y = d3.scale.ordinal()
   .rangeRoundBands([0, height], .1, 0);
  y.domain(data.map(function(d) { return d.id; }));
  yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");
}

var dataset;
var original_root;

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .attr("id","main")
    .attr("class", "main")
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .on("mouseleave", function() {
        $(".legend rect").removeClass('hover').tooltip('hide');
      });

var legend = d3.select("#chart").append("svg")
    .attr("width", "350")
    .attr("id", "legend")
    .attr("class", "main")
  .append("g")
    .attr("transform","translate("+margin.right+","+ margin.top + ")");

function calculateTopicMap(data, scale, sortFn){
  data.forEach(function(d) {
    var sizeFactor = (scale) ? d.prob : 1.0
    var x0 = 0;
    if (sortFn) d.topicMap = d3.keys(original_root.topics)
      .sort(sortFn)
      .map(function(name) { return {name: name, x0: x0, x1: x0 += +(d.topics[name]*sizeFactor) }; });
    else // maintain sort order
      d.topicMap = d.topicMap.map(function (topic) { return topic.name; })
        .map(function(name) { return {name: name, x0: x0, x1: x0 += +(d.topics[name]*sizeFactor) }; });
  });
  
}

var url;
if (roottopic) url = "topics/" + roottopic + '.json';
else if (q) url = "word_docs.json?q=" + q.replace(/ /g, '|');
else if (docid) url = "docs_topics/" + encodeURIComponent(docid) + '.json';
else url = null;


var n = inpho.util.getValueForURLParam('n');
if (n) url += "?n=" + n;

var tops;
if (url) 
d3.json(url, function(error, data) {
  $('#status .bar').css('width', '50%').text('Loading topics...');
  if (error) {
    $('#status .progress-bar').removeClass('active progress-bar-striped');
    var errormsg;
    
    if (roottopic) errormsg = "Invalid topic: " + roottopic + ".";
    else if (q) errormsg = "Search terms not in model, try a different query."
    else errormsg = "Invalid document: " + docid + ".";

    $('#status .bar').addClass('progress-bar-danger').text(errormsg);
    return false;
  }
  console.log(data);
  d3.json("topics.json", function(error_top, topics) {
    $('#status .bar').css('width', '75%').text('Rendering chart...');
    if (error_top) {
        $('#status .progress-bar').removeClass('active progress-bar-striped');
        $('#status .progress-bar-danger').addClass('progress-bar-error').text('Could not load topic list.');
        return false;
      }
        console.log(topics);
      $('#submit').text(d3.keys(topics).length + ' Topics');
      
  
    var legendCols = Math.max(Math.ceil(d3.keys(topics).length / Math.min(data.length, maxRows)), minCols);
    var legendFactor = Math.ceil(d3.keys(topics).length / legendCols);
    computeHeight(data,legendFactor);
    $("#chart #main").attr("height", height + margin.top + margin.bottom);
    $("#legend").attr("height", (legendFactor * 20) + margin.top + margin.bottom);
    computeWidth(legendCols);
  
  
    x.domain([0, 1.0]);
    tops = topics;
      //.sort();
    dataset = data;
    original_root = data[0];
    if (roottopic) docid = data[0]['doc'];
  
    calculateTopicMap(data, !($('.scale')[0].checked), function(a,b) {return data[0].topics[b] - data[0].topics[a];});
  
  
  
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(10,-10)")
        .call(xAxis)
      .append("text")
        //.attr("transform", "rotate(-120)")
        .attr("class", "axis_label")
        .attr("dy", "-2em")
        .style("text-anchor", "start")
        .text("Similarity to " + $('.title').first().text());
  
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .selectAll("text")
        .attr("class", function(d) { return (q == null && d == docid && roottopic == null) ? "primary" : "" })
        .on("click", function(d) { window.location.href = window.location.origin + window.location.pathname + "?doc=" + encodeURIComponent(d);})
  
    svg.select(".y.axis").selectAll("g")
        .insert("rect", ":first-child")
          .attr("x", -margin.left + 5)
          .attr("y", -9)
          .attr("width", margin.left-5)
          .attr("height", 18)
          .style("opacity", "0");
  
    var ticks = svg.select(".y.axis").selectAll("g")
        .on("mouseenter", function(d) { 
          $('text', this).attr('text-decoration', 'underline')
            .attr('font-weight', 'bold');     
          svg.selectAll(".doc")
            .filter(function(doc,i) { return doc.doc == d})
            .attr("class", function(d) { return ((q == null && d.doc == docid && roottopic == null) ? "doc primary" : "doc") + " hover"}); 
          })
        .on("mouseleave", function(d) { 
          $('text',this).removeAttr('text-decoration')
            .removeAttr('font-weight'); 
          svg.selectAll(".doc")
            .filter(function(doc,i) { return doc.doc == d})
            .attr("class", function(d) { return (q == null && d.doc == docid && roottopic == null) ? "doc primary" : "doc"}); 
          });
  
    for (var i = 0; i < icons.length; i++) {
      icon_fns[icons[i]](ticks,i, data);
    }
    
    // draw total bar
    var doc = svg.selectAll("doc")
        .data(data)
      .enter().append("g")
        .attr("class", function(d) { return (q == null && d.doc == docid && roottopic == null) ? "doc primary" : "doc"})
        .attr("transform", function(d) { return "translate(10," + y(d.id) + ")";  })
        .on("mouseover", function(d) {
            var tick = $("text:contains(" + d.id +")")
              .filter(function() { return $(this).text().trim() == d.id })
              .attr("font-weight", "bold");
            icons.reduce(function(prev,cur) {
              return prev.next(".{0}Icon".format(cur)).css('opacity', '1.0');
            }, tick);
          })
        .on("mouseout", function(d) {
            var tick = $("text:contains(" + d.id +")")
              .filter(function() {return $(this).text().trim() == d.id })
              .attr("font-weight", "normal");
            icons.reduce(function(prev, cur) {
              return prev.next(".{0}Icon".format(cur)).css('opacity', '');
            }, tick);
          })
        ;

  
    // Draw topic bars
    doc.selectAll("rect")
        .data(function(d) { return d.topicMap; })
      .enter().append("rect")
        .attr("height", y.rangeBand()/2.75)
        .attr("x", function(d) { return x(d.x0); })
       .attr("y", 10)
        .attr("width", function(d) { return x(d.x1) - x(d.x0); })
        .attr("class", function(d) { return "top_" + d.name; })
        .on("mouseover", function(d) {
            // SVG element z-index determined by render order, not style sheet
            // so element must be reappended to the end on hover so border 
            // is not occluded
            var parent = $(this).parent();
            $(this).detach().appendTo(parent);
            $(".docLabel", parent).detach().appendTo(parent);
            $(".docLabel", parent).addClass("hover");
            $('.legend rect').not('.top_' + d.name).tooltip('hide');
            $(".top_" + d.name).addClass('hover');
            $('.legend rect.top_' + d.name).tooltip('show');
          })
        .on("mouseout", function(d) {
            var parent = $(this).parent();
            $(".docLabel", parent).removeClass("hover");
            $(".top_" + d.name).removeClass('hover');
          })
        .on("click", function(d) {
          //Handles when to update the descriptor based off which mode it is in and what topic bar was clicked on.
          //Indicates whether the model is sorted by proportion of a specific topic or not.
          if (roottopic == null) {
            $("#focalDoc").text("Top 40 documents most similar to the focal document sorted by proportion of topic " + d.name);
          } else if (roottopic == d.name) {
            topDoc.style.display = 'none';
            $("#focalDoc").text("Top 40 documents most similar to topic " + roottopic);
          } else {
            topDoc.style.display = 'block';
            $("#focalDoc").text("Top 40 documents most similar to topic " + roottopic + " sorted by proportion of topic " + d.name);
          }
          topicSort(d.name); })
        .style("fill", function(d) { return barColors(topics[d.name]['color'], d.name, svg); });

    doc.append("text")
          .text(function(d) { return d.label; })
          .attr("class","docLabel")
          .attr("dx", "3")
          .attr("dy", "8")
        .filter(function(d) { return q && (d.label.indexOf(q) >= 0);})
        .each(function(d) {
            if (q) {
              var splits = q.split(' ');
              var new_html = d.label;
              for (var i = 0; i < splits.length; i++) {
                var myRe = new RegExp(splits[i], 'gi');
                new_html = new_html.replace(myRe, '<tspan style="font-weight: bold;>$&</tspan>');
                $("text:contains("+d.label+")").html(new_html);
              }
            }
          });

    var legendElts = legend.selectAll(".legend")
        .data(data[0].topicMap.map(function(t) { return t.name;}))
      .enter().append("g")
        .attr("class", function(d) { return "legend top_" + d; })
        .attr("transform", function(d, i) { return "translate("+(55 * Math.floor(i / legendFactor))+"," + (20*(i % legendFactor)) + ")"; });
  
    legendElts.append("rect")
        .attr("width", 18)
        .attr("height", 18)
        .attr("class", function(d) { return "top_" + d; })
        .style("fill", function(d) { return topics[d]['color']; })
        //.attr("data-toggle", "tooltip")
        .attr("data-placement", "right")
        .attr("title", function(d) { 
          return "<strong>Topic {0}:</strong>".format(d) + "<br />"
            + d3.keys(topics[d].words).sort(function(a,b) {
              if (topics[d].words[a] > topics[d].words[b])
                return -1;
              else if (topics[d].words[a] < topics[d].words[b])
                return 1;
              else
                return 0;
            }).join(", ") + ", ..."; })
        .on("click", function(d) {
          //Handles when to update the descriptor based off which mode it is in and what topic bar was clicked on.
          //Indicates whether the model is sorted by proportion of a specific topic or not.
          if (roottopic == null) {
            $("#focalDoc").text("Top 40 documents most similar to the focal document sorted by proportion of topic " + d);
          } else if (roottopic == d) {
            topDoc.style.display = 'none';
            $("#focalDoc").text("Top 40 documents most similar to topic " + roottopic);
          } else {
            topDoc.style.display = 'block';
            $("#focalDoc").text("Top 40 documents most similar to topic " + roottopic + " sorted by proportion of topic " + d);
          }
          topicSort(d); })
        .on("mouseover", function(d) {
            $(".top_" + d).addClass('hover').tooltip('show');
          })
        .on("mouseout", function(d) {
            $(".top_" + d).removeClass('hover').tooltip('hide');
          });
  
    $(".legend rect").tooltip({container:'body', trigger: 'manual', animation: false, html: true});
  
    legendElts.append("text")
        .attr("dx", -6)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) { return d; });
  
  
    legend.append("text")
        .attr("dx", -6)
        .attr("dy", "-.35em")
        .attr("font-weight", "bold")
        .style("text-anchor", "end")
        .text(d3.keys(topics).length);
    legend.append("text")
        //.attr("transform", "rotate(-120)")
        .attr("class", "axis_label")
        .attr("dy", "-.35em")
        .attr("font-weight", "bold")
        .style("text-anchor", "start")
        .text("Topics");
    legend.append("text")
        //.attr("transform", "rotate(-120)")
        .attr("class", "axis_label")
        .attr("dy", "-.45em")
        .attr("dx", "5em")
        .attr("font-size", "9.5px")
        .style("text-anchor", "start")
        .style("overflow-wrap", "normal")
        .text("ordered by proportion of T in " + (docid ? "focal document" : "corpus"));

    d3.select(window).on('resize', resize);
  
    function resize() {
      computeWidth(legendCols);
  
      /* Update the axis with the new scale */
      svg.select('.x.axis')
        .call(xAxis);
  
      doc.selectAll('rect')
        .attr("x", function(d) { return x(d.x0); })
        .attr("width", function(d) { return x(d.x1) - x(d.x0); });    }
  
      d3.select(".sort").on("change", alphabetSort);
      
      $('#status .bar').addClass('bar-success').css('width', '100%').text("Complete!");
      setTimeout(function() { 
        $('#status').hide(500);
        setTimeout(function() {$('#controls').css({'top' : $('#legend').height() + $('#legend').position().top}).show();}, 500);
        } , 500);
    
      $(window).on("scroll", scrollLegend);
      scrollLegend = function() {
        var scrollPos = $(window).scrollTop();
        var chartHeight = $('#chart').position().top;
        var legendHeight = $('#legend').height();
        var heightFac = -60;
        if((scrollPos - chartHeight - margin.top - heightFac) <= 0) {
          $('#legend').css({'position': 'absolute', 'top' : chartHeight});
          $('#controls').css({'position': 'absolute', 'top' : legendHeight + chartHeight});
        } else if ((scrollPos - chartHeight - heightFac) < (margin.top)) {
          $('#legend').css({'position': 'absolute', 'top' : scrollPos + heightFac});
          $('#controls').css({'position': 'absolute', 'top' : legendHeight+ scrollPos + heightFac});
        } else {
          $('#legend').css({'position': 'fixed', 'top' : heightFac});
          $('#controls').css({'position': 'fixed', 'top' : legendHeight + heightFac});
        }}
    
      for (var i = 0; i < icons.length; i++) {
        $(".{0}Icon".format(icons[i])).tooltip({placement: 'top', title: icon_tooltips[icons[i]], container: 'body', html: true, animation: false});
      }
    }); 
  });

  function scaleTopics() {
    var numTopics = dataset[0].topics.length;
    var delay = function(d, i) { return i * (500/numTopics); },
        negdelay = function(d, i) { return (numTopics-i) * (500/numTopics); };

    calculateTopicMap(dataset, !this.checked);

    $(".doc").each(function(i,elt) {
        $(elt).children()
          .sort(function(a,b) { return $(a).attr('x') - $(b).attr('x'); })
          .each(function(j,child) {
            $(child).detach().appendTo($(elt));
        })
      });

    svg.selectAll(".doc")
      .selectAll("rect")
      .data(function(d) { return d.topicMap; })
      .style("fill", function(d) { return barColors(tops[d.name]['color'], d.name, svg); })
      /*.on("mouseover", function(d) {
          // SVG element z-index determined by render order, not style sheet
          // so element must be reappended to the end on hover so border 
          // is not occluded
          var parent = $(this).parent();
          $(this).detach().appendTo(parent);
          $(".docLabel", parent).detach().appendTo(parent);
          $('.legend rect').not('.top_' + d.name).tooltip('hide');
          $(".top_" + d.name).addClass('hover');
          $('.legend rect.top_' + d.name).tooltip('show');
        })
      .on("mouseout", function(d) {
          $(".top_" + d.name).removeClass('hover');
        })*/
      .transition().duration(500).ease("linear").delay(this.checked ? delay : negdelay)
      .attr("x", function(d) { return x(d.x0); })
      .attr("width", function(d) { return x(d.x1) - x(d.x0); })
      .attr("class", function(d) { return "top_" + d.name; });

    svg.selectAll(".x.axis text.axis_label").text(this.checked ? 
      "Proportion of document assigned to topic" : 
      ("Similarity to " + $('.title').first().text()));
  }

  d3.select(".scale").on("change", scaleTopics);
  function sortDataset(sortFn) {
    dataset = dataset.sort(sortFn);

    var y0 = y.domain(dataset
        .map(function(d) { return d.id; }))
        .copy();

    var transition = svg.transition().duration(500),
        delay = function(d, i) { return i * 25; };

    transition.selectAll(".doc")
        .delay(delay)
        .attr("transform", function(d) { return "translate(10," + y(d.id) + ")"; });
        //.attr("y", function(d) { return y(d.id); });

    transition.select(".y.axis")
        .call(yAxis)
      .selectAll("g")
        .selectAll("text")
        .delay(delay);
  }

  function alphabetSort() {
    // Copy-on-write since tweens are evaluated after a delay.
    if (this.checked)
      sortDataset(function(a, b) { return d3.ascending(a.label, b.label); });
    else
      sortDataset(function(a, b) { return b.prob - a.prob; });
  }

  function resetTopicSort() {
    $('.reset').attr('disabled',true);
    $('.topicsort').attr('disabled',true);
    $('.selected').removeClass('selected');
    $('.topdoc').text('Click a topic segment below to find related documents.');
    $('.topdoc').removeClass('btn-primary');
    $('.topdoc').addClass('btn-default');
    $('.topdoc').attr('disabled', 'disabled');
    if (!($('.sort')[0].checked))
      sortDataset(function(a,b) { return b.prob - a.prob; });

    redrawBars(function(a,b) { return original_root.topics[b] - original_root.topics[a]; });
  }

  function topicSort(topic) {
    // Copy-on-write since tweens are evaluated after a delay.
    $('.sort').removeAttr('checked');
    if (topic) {
      sortDataset(function(a, b) { return b.topics[topic] - a.topics[topic]; });
      $('.selected').removeClass('selected');
      $(".top_" + topic).addClass('selected');
      $('.reset').removeAttr('disabled');
      if (topic == roottopic) {
        $('.topdoc').css('font-weight', 'bold');
        $('.topdoc').removeClass('btn-primary');
        $('.topdoc').addClass('btn-default');
      } else {
        $('.topdoc').css('font-weight', 'normal');
        $('.topdoc').removeClass('btn-default');
        $('.topdoc').addClass('btn-primary');
      }
      $('.topdoc').removeAttr('disabled');
      $('.topdoc').text('Retrieve Documents for Topic ' + topic);
      $('.topdoc').click(function() { location.href = location.origin + location.pathname + '?topic=' + topic;});
      $('.topdoc').mouseenter(function() {
          $('.legend rect').not('.top_' + topic).tooltip('hide');
          $(".legend rect.top_" + topic).tooltip('show'); });
      $('.topdoc').mouseleave(function() { $(".top_" + topic).tooltip('hide'); });

    } else {
      $('.selected').removeClass('selected');
      sortDataset(function(a, b) { return b.prob - a.prob; });
    }


    var sortFn = function(a,b) {
      if (a == topic) return -1;
      else if (b == topic) return 1;
      else return dataset[0].topics[b] - dataset[0].topics[a];
      //else return original_root.topics[b] - original_root.topics[a];
    } 
    redrawBars(sortFn);
  }

  function redrawBars(sortFn) { 
    $("#legend .hover").removeClass("hover");
    var numTopics = dataset[0].topics.length;
    var delay = function(d, i) { return i * (1000/numTopics); },
        negdelay = function(d, i) { return (numTopics-i) * (1000/numTopics); };
    calculateTopicMap(dataset, !($('.scale')[0].checked), sortFn);
    
    svg.selectAll(".doc")
      .selectAll("rect")
      .data(function(d) { return d.topicMap; })
      .style("fill", function(d) { return barColors(tops[d.name]['color'], d.name, svg); })
      /*
      .on("mouseover", function(d) {
          // SVG element z-index determined by render order, not style sheet
          // so element must be reappended to the end on hover so border 
          // is not occluded
          var parent = $(this).parent();
          $(this).detach().appendTo(parent);
          $(".docLabel", parent).detach().appendTo(parent);
          $('.legend rect').not('.top_' + d.name).tooltip('hide');
          $(".top_" + d.name).addClass('hover');
          $('.legend rect.top_' + d.name).tooltip('show');
        })
      .on("mouseout", function(d) {
          $(".top_" + d.name).removeClass('hover');
        })*/
      .transition().duration(1000).ease("linear").delay(this.checked ? delay : negdelay)
      .attr("x", function(d) { return x(d.x0); })
      .attr("width", function(d) { return x(d.x1) - x(d.x0); })
      .attr("class", function(d) { return "top_" + d.name; });

  }

  // From StackOverflow: https://stackoverflow.com/a/21648508
  function hexToRgbA(hex, a){
    var c;
    if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
        c= hex.substring(1).split('');
        if(c.length== 3){
            c= [c[0], c[0], c[1], c[1], c[2], c[2]];
        }
        c= '0x'+c.join('');
        return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+',' + a + ')';
    }
    throw new Error('Bad Hex');
  }

  function barColors(myColor, myId, svg) {
    var mainGradient = svg.append('linearGradient')
        .attr('id', myId);
    mainGradient.append('stop')
        .attr('stop-color', myColor)
        .attr('offset', '0');
    mainGradient.append('stop')
        .attr('stop-color', hexToRgbA(myColor, .7))
        .attr('offset', '1');
    return "url(#" + myId + ")";
  }


fingerprint.host = '../';

$('#home-link').attr('href', '../');
$('#cluster-link').attr('href', '../topics');
$('.topic-link').each(function(i,elt) {
    var url = '../' + $(elt).attr('href');
    if(docid) url += '?doc=' + docid;
    $(this).attr('href', url);
  }); 

