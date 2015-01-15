'use strict';

var App = App || {};

App = {
    init: function () {
        // App.dataTables();
    },
    dataTables: function () {
        $('table').dataTable();
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
			),	function(x){ return x;}
		);

		// parse the amounts to float
		_.each(expends, function(d,i){
			expends[i].total=parseFloat(d.total);
		});

		_.each(contribs,function(d,i){
			contribs[i].total = parseFloat(d.total);
		});
			
		// D3 voodoo to add thrirght number of divs in the right order
		var chartContainer = d3.select("#moneyFlowViz");
    	var width = $("#moneyFlowViz").width();

		var chartScale = d3.scale.linear()
		    .range([0, width])
		    .domain([0, d3.max(_.union(_.pluck(contribs,'total'),_.pluck(expends, 'total')))]);

		var yeargroups = chartContainer.selectAll('div')
			.data(years_data)
		.enter().append('div')
			.classed('yeargroup',true);

		yeargroups.append('span')
			.classed('yeartext', true)
			.text(function(d){return d;});

		yeargroups.append('div')
			.classed('contribBar',true)
			.style('width',function(d){return chartScale(_.find(contribs, function(x){ return x.year==d; }).total)+'px';})
			.style('background-color','grey');

		yeargroups.append('span')
			.text(function(d){return '$' + _.find(contribs, function(x){ return x.year==d; }).total;});

		yeargroups.append('div')
			.classed('expendBar',true)
			.style('width',function(d){return chartScale(_.find(expends, function(x){ return x.year==d; }).total)+'px';})
			.style('background-color','lightgrey');

		yeargroups.append('span')
			.text(function(d){return '$' + _.find(expends, function(x){ return x.year==d; }).total;});

    }
};

jQuery(document).ready(function($) {
    App.init();
});