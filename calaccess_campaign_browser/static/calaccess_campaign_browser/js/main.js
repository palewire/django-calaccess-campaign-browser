'use strict';

var App = App || {};

App = {
    init: function () {
        App.dataTables();
    },
    dataTables: function () {
        //$('table').dataTable();
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

    },
    contribViz: function (filings) {
        var dataTable = dc.dataTable("#dc-table-graph");
      var timeChart = dc.barChart("#dc-time-chart");

      var data = filings;

      data.forEach(function(d){
        d.num = d.filing_id_raw;
        d.dtg = d.date_filed;
        d.date = d3.time.format("%Y-%m-%d").parse(d.date_filed);
        d.ft = d.form_type;
        d.pd = d.start_date + " - " + d.end_date;
        d.contributions = d.summary.total_contributions;
        d.expenditures = d.summary.total_expenditures;
        d.debts = d.summary.outstanding_debts;
      });

      var info = crossfilter(data);
      var timeDimension = info.dimension(function(d){
        return d.date;
      });
      var minDate = d3.time.day.offset(timeDimension.bottom(1)[0].date,-1);
      var maxDate = d3.time.day.offset(timeDimension.top(1)[0].date,1);
      var width = 880;
      var margins = {top: 10, right: 10, bottom: 20, left: 80};
      var contrValueGroupCount = timeDimension.group()
          .reduceSum(function(d) { return d.contributions; });


      var xScale = d3.time.scale()
                     .domain([minDate,maxDate])
                     .rangeRound([0, width - margins.left - margins.right]);

      timeChart.width(width)
      .height(150)
      .margins(margins)
      .dimension(timeDimension)
      .group(contrValueGroupCount)
      .transitionDuration(500)
      .centerBar(true)
      .x(xScale)
      .elasticY(true)
      .xAxis().tickFormat();



      dataTable.dimension(timeDimension)
                .group(function(d){return "Chart"})
                .size(13)
                .columns([
                  function(d){ return d.num; },
                  function(d){ return d.dtg; },
                  function(d){ return d.ft; },
                  function(d){ return d.pd; },
                  function(d){ return d.contributions; },
                  function(d){ return d.expenditures; },
                  function(d){ return d.debts; },
                  ])
                .sortBy(function(d){ return d.dtg; })
                .order(d3.ascending);

      dc.renderAll();
    }
};

jQuery(document).ready(function($) {
    App.init();
});