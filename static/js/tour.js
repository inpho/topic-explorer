var tour = new Tour({
  steps: [
    {
      element: "#doc",
      title: "Document Selection",
      content: "There are a few ways to select a new focal document. One is by typing in a few letters in the focal document entry area.",
      placement: "top"
    }, {
      element: "#randomDoc",
      title: "Random Document Selection",
      content: "You can also click the   <span class='glyphicon glyphicon-random'></span>    button to the right of the focal document entry area for a random document.",
      placement: "top"
    }, {
      element: "#tutorial",
      title: "Random Document Selection",
      content: "You may use this button to visualize the focal document and you may use the dropdown menu attached to the button to switch to a model with a different number of topics.",
      placement: "top"
    }, {
      element: "#visualize_button",
      title: "Continuation of Tutorial",
      content: "From this point onwards, you can either exit the tutorial, type in a document yourself and click the 'Visualize' button, or you can click 'Next' and allow the tutorial to pick a document for you.",
      placement: "bottom",
      onNext: function(tour) {
        $("#randomDoc").click();
        //console.log(document.getElementById("#doc").value);
        //$("#submit").click();
        
        setTimeout(function () {
          $("#submit").click();
        }, 500);
        /*
        if(tour.started() && !tour.ended())
        {
          tour.init();
          tour.start();
        }
        */

      },
      
    }, {
      element:"#chart",
      title: "Hypershelf",
      content: "The Hypershelf shows up to 40 documents that are most similar to the focal document. Each document is represented by a bar whose colors show the mixture and proportions of topics assigned to each document by the training process. The relative lengths of the bars indicate the degree of similarity to the focal document according to the topic mixtures.",
      placement: "top",
      //delay: 1000
      //autoscroll: false,
      //smartPlacement: false

    },
    {
      element:"#legend",
      title: "Legend",
      content: "This is a legend designed to navigate and manipulate data on the Hypershelf easier. You can click on any of the colored squares to focus on a particular topic, alphabetize the papers, and normalize the topic bars.",
      placement:"left"
    },
    {
      element: "#docDemonstration",
      title: "Documents",
      content:"The Hypershelf shows up to 40 documents that are most similar to the focal document. Each document is represented by a bar whose colors show the mixture and proportions of topics assigned to each document by the training process. The relative lengths of the bars indicate the degree of similarity to the focal document according to the topic mixtures.",
      placement:"bottom"
    },
    
    {
      element: "#home-page",
      title: "Home Page",
      content: "Click on this to return to the home page",
      placement: "bottom"
    }
    
  ]
});
tour.init();

if(!tour.ended())
        {
          tour.init();
          tour.start();
        }

// start tour
jQuery(document).ready(function ($){
  $('#tour-button').click(function () {
    tour.restart();
  });
});

