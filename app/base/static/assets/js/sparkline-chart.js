var values = [[],[],[],[],[]],
    options = {
        width: '150px',
        height: '30px',
        lineColor: $white,
        lineWidth: '2',
        spotRadius: '2',
        highlightLineColor: $gray,
        highlightSpotColor: $gray,
        spotColor: false,
        minSpotColor: false,
        maxSpotColor: false
    };
        
function drawSparkLines_(){
    options.lineColor = $green;
    options.fillColor = 'rgba(86, 188, 118, 0.1)';
    $('#sqf-spark').sparkline(data_5, options );
    options.lineColor = $orange;
    options.fillColor = 'rgba(234, 200, 94, 0.1)';
    $('#ping-spark').sparkline(data_4, options );
    options.lineColor = $blue;
    options.fillColor = 'rgba(106, 141, 167, 0.1)';
    $('#traffic23-spark').sparkline(data_2, options );
    options.lineColor = $red;
    options.fillColor = 'rgba(229, 96, 59, 0.1)';
    $('#traffic24-spark').sparkline(data_3, options );
    options.lineColor = $white;
    options.fillColor = 'rgba(255, 255, 255, 0.1)';
    $('#uptime-spark').sparkline(data_1, options );
}

drawSparkLines_();