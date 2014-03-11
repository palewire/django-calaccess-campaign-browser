'use strict';

var App = App || {};

App = {
    createCalendar: function (selector, data) {
        var cal = new CalHeatMap();
        cal.init({
            // passed in values
            itemSelector: selector,
            start: data.startDate(),
            data: data.data,

            // formatting
            domain: 'year',
            subDomain: 'x_day',
            //subDomainTextFormat: "%d",
            tooltip: true,
            domainMargin: [0, 10, 0, 0],
            legend: [100, 1000, 10000, 10000],
            range: App._determineRangeSize(),
            previousSelector: '#previous',
            nextSelector: '#next',
        });
    },
    clearCalendar: function (selector) {
        // This is busted kind
        var elements = document.querySelector(selector).children;

        _.each(elements, function (el) {
            el.remove();
        });
    },
    _determineRangeSize: function () {
        var browserWidth = document.documentElement.clientWidth;

        if (browserWidth <= 420) {
            return 3;
        } else {
            // Desktop
            return 5
        }
    }
};