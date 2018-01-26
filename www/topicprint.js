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

function computeHeight(data, numLegendRows) { 
  height = (data.length * 30);// - margin.top - margin.bottom;
  y = d3.scale.ordinal()
   .rangeRoundBands([0, height], .1, 0);
  y.domain(data.map(function(d) { return d.id; }));
  yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");
}

//The calculateTopicMap function was changed to work with one document
//and multiple documents instead of having two functions for both.
function calculateTopicMap(data, scale, sortFn){
      data.forEach(function(d) {
        var sizeFactor = (scale) ? d.prob : 1.0
        var x0 = 0;
        var dTopics = undefined === original_root ? d.topics : original_root.topics; //fixed syntax for undefined usage
        if (sortFn) d.topicMap = d3.keys(dTopics)
          .sort(sortFn)
          .map(function(name) { return {name: name, x0: x0, x1: x0 += +(dTopics[name]*sizeFactor) }; });
        else d.topicMap = d3.keys(dTopics)
          .map(function(name) { return {name: name, x0: x0, x1: x0 += +(dTopics[name]*sizeFactor) }; });
      });
      
    }

function resize() {
  computeWidth(legendCols);

  /* Update the axis with the new scale */
  svg.select('.x.axis')
    .call(xAxis);
  
  doc.selectAll('rect')
    .attr("x", function(d) { return x(d.x0); })
    .attr("width", function(d) { return x(d.x1) - x(d.x0); });
}

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
    .style("fill", function(d) { return tops[d.name]['color']; })
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
    $('.topdoc').text('Top Documents for Topic ' + topic);
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
    .style("fill", function(d) { return tops[d.name]['color']; })
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
        var full_explorer_url = host+"/?doc="+docid;
      
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

