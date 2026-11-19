// Define module using Universal Module Definition pattern
// https://github.com/umdjs/umd/blob/master/returnExports.js

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // Support AMD. Register as an anonymous module.
    // EDIT: List all dependencies in AMD style
    define(['d3'], factory);
  }
  else if (typeof exports === 'object') {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like environments that support module.exports,
    // like Node.
    // EDIT: Pass dependencies to factory function
    module.exports = factory(require('d3'));
  }
  else {
    // No AMD. Set module as a global variable
    // EDIT: Pass dependencies to factory function
    root.d3.promise = factory(root.d3);
  }
}(this,
//EDIT: The dependencies are passed to this function
function (d3) {
  //---------------------------------------------------
  // BEGIN code for this module
  //---------------------------------------------------

  var d3Promise = (function(){

    function promisify(caller, fn){
      return function(){
        var args = Array.prototype.slice.call(arguments);
        return new Promise(function(resolve, reject){
          var callback = function(error, data){
            if(error){
              reject(Error(error));
              return;
            }
            resolve(data);
          };
          fn.apply(caller, args.concat(callback));
        });
      };
    }

    var module = {};

    ['csv', 'tsv', 'json', 'xml', 'text', 'html'].forEach(function(fnName){
      module[fnName] = promisify(d3, d3[fnName]);
    });

    return module;
  }());

  // append to d3
  d3.promise = d3Promise;

  // return module
  return d3Promise;

  //---------------------------------------------------
  // END code for this module
  //---------------------------------------------------
}));