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
            .style("fill", function(d) { return topics[d.name]['color']; });
      
      
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

