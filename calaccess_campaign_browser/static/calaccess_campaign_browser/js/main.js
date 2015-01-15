'use strict';

var App = App || {};

App = {
    init: function () {
        App.dataTables();
    },
    dataTables: function () {
<<<<<<< HEAD
        $('table').dataTable();
=======
        $("table").stupidtable({
	        "currency":function(a,b){

	            var aNum = a.replace('$', '').replace(/,/g, '');
	            var bNum = b.replace('$', '').replace(/,/g, '')

	            return parseInt(aNum,10) - parseInt(bNum,10);
	          },
	        "date":function(a,b){
	          var year1 = parseInt(a.substring(0,4));
	          var month1 = parseInt(a.substring(7,5)) - 1;
	          var day1 = parseInt(a.substring(10,8));

	          var year2 = parseInt(b.substring(0,4));
	          var month2 = parseInt(b.substring(7,5)) - 1;
	          var day2 = parseInt(b.substring(10,8));

	          var date1 = new Date(year1, month1, day1);
	          var date2 = new Date(year2, month2, day2);

	          return date1 - date2;
	        }
	    });
>>>>>>> fe90971b529dde7969012d42505b288b4542f1fc
    },
    chartViz: function(contribs, expends) {

    	// data massaging
    	var data = [];
		var years_data = _.sortBy( 
			_.uniq(
				_.union(
					_.pluck(contribs, 'year'),
					_.pluck(expends, 'year')
				)
			),	function(x){ return -x;}
		);

		// parse the amounts to float, then round off to int
		_.each(expends, function(d,i){
			expends[i].total=Math.floor(parseFloat(d.total));
		});

		_.each(contribs,function(d,i){
			contribs[i].total = Math.floor(parseFloat(d.total));
		});
			
		// D3 voodoo to add thrirght number of divs in the right order
		var chartContainer = d3.select("#moneyFlowViz");
    	var width = $("#moneyFlowViz").width();

		var chartScale = d3.scale.linear()
		    .range([0, width*.8])
		    .domain([0, d3.max(_.union(_.pluck(contribs,'total'),_.pluck(expends, 'total')))]);

		var formatter = d3.format("0,000");

		var yeargroups = chartContainer.selectAll('div')
			.data(years_data)
		.enter().append('div')
			.classed('yeargroup',true);

		yeargroups.append('span')
			.classed('yeartext', true)
			.text(function(d){return d;});

		var barContainer = yeargroups.append('span')
			.classed('barContainer', true);

		var contribDivs = barContainer.append('div')
			.classed('contrib',true);

		contribDivs.append('div')
			.classed('bar',true)
			.style('width',function(d){return chartScale(_.find(contribs, function(x){ return x.year==d; }).total)+'px';})
			.classed('series1',true);

		contribDivs.append('span')
			.text(function(d){return '$' + formatter(_.find(contribs, function(x){ return x.year==d; }).total);});

		var expendDivs = barContainer.append('div')
			.classed('expend',true);

		expendDivs.append('div')
			.classed('bar',true)
			.style('width',function(d){return chartScale(_.find(expends, function(x){ return x.year==d; }).total)+'px';})
			.classed('series2',true);

		expendDivs.append('span')
			.text(function(d){return '$' + formatter(_.find(expends, function(x){ return x.year==d; }).total);});

    }
};

jQuery(document).ready(function($) {
    App.init();
});