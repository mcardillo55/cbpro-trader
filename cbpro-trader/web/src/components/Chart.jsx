import React from 'react';
import * as LightweightCharts from 'lightweight-charts';

function Chart (props) {
    const ref = React.useRef(null);
    const [chart, setChart] = React.useState(null);
    const [initialZoomSet, setInitialZoomSet] = React.useState(false); // Tracks if we have set the initial zoom yet
    const [candlestickSeries, setCandlestickSeries] = React.useState(null);
    const { candlesticks } = props;
    let clientWidth, clientHeight;

    clientWidth = ref.current && ref.current.clientWidth;
    clientHeight = ref.current && ref.current.clientHeight;

    React.useEffect(() => {
        if (!chart) {
            setChart(LightweightCharts.createChart(ref.current, {
            width: 0,
            height: 0,
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
                    timeVisible: true,
                    borderColor: 'rgba(197, 203, 206, 0.8)',
                },
            }));
        }
    });

    React.useEffect(() => {
        if(chart) {
            setCandlestickSeries(chart.addCandlestickSeries({
                upColor: '#53b987',
                downColor: '#eb4d5c',
                borderDownColor: '#eb4d5c',
                borderUpColor: '#53b987',
                wickDownColor: '#eb4d5c',
                wickUpColor: '#53b987',
            }))
        };
    }, [chart]);

    React.useEffect(() => {
        if (candlestickSeries) {
            candlestickSeries.setData(candlesticks);
        }

        if (!initialZoomSet && chart && chart.timeScale().getVisibleRange()) {
            let timeDiff = candlesticks[candlesticks.length -1]['time'] - candlesticks[candlesticks.length -2]['time'];
            chart.timeScale().setVisibleRange({
                from: candlesticks[candlesticks.length -1]['time'] - (timeDiff * 30), // Show 30 candles by default
                to: candlesticks[candlesticks.length -1]['time'],
            })
            setInitialZoomSet(true);
        }
    }, [candlesticks]);

    function resizeChart() {
        if (chart) {
            chart.resize(0, 0);
            chart.resize(ref.current.clientWidth, ref.current.clientHeight);
        }
    }

    window.addEventListener('resize', () => resizeChart());

    React.useEffect(() => resizeChart(), [window.innerHeight, window.innerWidth, clientHeight, clientWidth]);

    return (
        <div id="chart" ref={ref}>
        </div>
    )
}

export default Chart;