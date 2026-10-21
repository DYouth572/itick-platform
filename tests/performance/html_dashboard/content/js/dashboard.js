/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 66.66666666666667, "KoPercent": 33.333333333333336};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.55, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "02_GET_Event_Detail"], "isController": false}, {"data": [0.0, 500, 1500, "01_GET_List_Events"], "isController": false}, {"data": [0.65, 500, 1500, "03_POST_Book_Tickets_Concurrency"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 300, 100, 33.333333333333336, 432.7933333333332, 5, 789, 607.5, 717.0, 746.8499999999999, 781.9300000000001, 15.92187665852882, 23.032818968262394, 6.675578494851927], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["02_GET_Event_Detail", 100, 0, 0.0, 8.409999999999997, 5, 14, 8.0, 11.0, 12.0, 13.989999999999995, 6.518479890489537, 8.83559578906199, 2.5399155042044197], "isController": false}, {"data": ["01_GET_List_Events", 100, 100, 100.0, 715.8700000000002, 709, 764, 714.0, 717.0, 747.3999999999999, 763.96, 6.222388152572957, 14.875396677244725, 2.4123907193080703], "isController": false}, {"data": ["03_POST_Book_Tickets_Concurrency", 100, 0, 0.0, 574.1000000000001, 257, 789, 607.5, 746.7, 772.8, 788.9399999999999, 56.75368898978434, 33.697502837684446, 27.268374006810443], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["The operation lasted too long: It took 714 milliseconds, but should not have lasted longer than 500 milliseconds.", 22, 22.0, 7.333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 711 milliseconds, but should not have lasted longer than 500 milliseconds.", 9, 9.0, 3.0], "isController": false}, {"data": ["The operation lasted too long: It took 717 milliseconds, but should not have lasted longer than 500 milliseconds.", 5, 5.0, 1.6666666666666667], "isController": false}, {"data": ["The operation lasted too long: It took 719 milliseconds, but should not have lasted longer than 500 milliseconds.", 2, 2.0, 0.6666666666666666], "isController": false}, {"data": ["The operation lasted too long: It took 751 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 760 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 716 milliseconds, but should not have lasted longer than 500 milliseconds.", 7, 7.0, 2.3333333333333335], "isController": false}, {"data": ["The operation lasted too long: It took 713 milliseconds, but should not have lasted longer than 500 milliseconds.", 20, 20.0, 6.666666666666667], "isController": false}, {"data": ["The operation lasted too long: It took 748 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 710 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 709 milliseconds, but should not have lasted longer than 500 milliseconds.", 2, 2.0, 0.6666666666666666], "isController": false}, {"data": ["The operation lasted too long: It took 736 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 764 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 712 milliseconds, but should not have lasted longer than 500 milliseconds.", 17, 17.0, 5.666666666666667], "isController": false}, {"data": ["The operation lasted too long: It took 715 milliseconds, but should not have lasted longer than 500 milliseconds.", 8, 8.0, 2.6666666666666665], "isController": false}, {"data": ["The operation lasted too long: It took 756 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}, {"data": ["The operation lasted too long: It took 718 milliseconds, but should not have lasted longer than 500 milliseconds.", 1, 1.0, 0.3333333333333333], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 300, 100, "The operation lasted too long: It took 714 milliseconds, but should not have lasted longer than 500 milliseconds.", 22, "The operation lasted too long: It took 713 milliseconds, but should not have lasted longer than 500 milliseconds.", 20, "The operation lasted too long: It took 712 milliseconds, but should not have lasted longer than 500 milliseconds.", 17, "The operation lasted too long: It took 711 milliseconds, but should not have lasted longer than 500 milliseconds.", 9, "The operation lasted too long: It took 715 milliseconds, but should not have lasted longer than 500 milliseconds.", 8], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": ["01_GET_List_Events", 100, 100, "The operation lasted too long: It took 714 milliseconds, but should not have lasted longer than 500 milliseconds.", 22, "The operation lasted too long: It took 713 milliseconds, but should not have lasted longer than 500 milliseconds.", 20, "The operation lasted too long: It took 712 milliseconds, but should not have lasted longer than 500 milliseconds.", 17, "The operation lasted too long: It took 711 milliseconds, but should not have lasted longer than 500 milliseconds.", 9, "The operation lasted too long: It took 715 milliseconds, but should not have lasted longer than 500 milliseconds.", 8], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
