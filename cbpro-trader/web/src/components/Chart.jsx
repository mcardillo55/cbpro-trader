import React from 'react';
import * as LightweightCharts from 'lightweight-charts';

let chart = null;
let candlestickSeries;

function Chart (props) {
    const ref = React.useRef(null);
    const { candlesticks } = props;

    React.useEffect(() => {
        if (!chart) {
            console.log(chart)
        chart = LightweightCharts.createChart(ref.current, {
            width: 1300,
          height: 700,
            layout: {
                backgroundColor: 'Transparent',
                textColor: 'rgba(255, 255, 255, 0.9)',
            },
            grid: {
                vertLines: {
                    color: 'rgba(197, 203, 206, 0.5)',
                },
                horzLines: {
                    color: 'rgba(197, 203, 206, 0.5)',
                },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(197, 203, 206, 0.8)',
            },
            timeScale: {
                borderColor: 'rgba(197, 203, 206, 0.8)',
            },
        });
        
        candlestickSeries = chart.addCandlestickSeries({
          upColor: '#53b987',
          downColor: '#eb4d5c',
          borderDownColor: '#eb4d5c',
          borderUpColor: '#53b987',
          wickDownColor: '#eb4d5c',
          wickUpColor: '#53b987',
        });
    }
    }, [])

    React.useEffect(() => {
        if (candlestickSeries) {
            candlestickSeries.setData(candlesticks);
        }
    }, [candlesticks]);

    return (
        <div id="chart" ref={ref}>
        </div>
    )
}

export default Chart;