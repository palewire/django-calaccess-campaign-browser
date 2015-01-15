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
		    .domain([0 , d3.max(_.union(_.pluck(contribs,'total'),_.pluck(expends, 'total')))]); //todo: update to handle negative stack

		var formatter = d3.format("0,000");

		var getAmountForYear = function(dataset, currYear){
			var record = _.find(dataset, function(x){ return x.year==currYear; });
			if(record){
				return record.total;
			}
			return 0;
		}

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
			.style('width',function(d){return chartScale(getAmountForYear(contribs, d))+'px';})
			.classed('series1',true);

		contribDivs.append('span')
			.text(function(d){return '$' + formatter(getAmountForYear(contribs, d));});

		var expendDivs = barContainer.append('div')
			.classed('expend',true);

		expendDivs.append('div')
			.classed('bar',true)
			.style('width',function(d){return chartScale(getAmountForYear(expends, d))+'px';})
			.classed('series2',true);

		expendDivs.append('span')
			.text(function(d){return '$' + formatter(getAmountForYear(expends, d));});

    }
};

jQuery(document).ready(function($) {
    App.init();
});