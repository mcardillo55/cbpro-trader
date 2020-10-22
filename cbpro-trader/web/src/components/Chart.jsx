import React from 'react';
import * as LightweightCharts from 'lightweight-charts';
import Tooltip from './Tooltip';

function Chart (props) {
    const ref = React.useRef(null);
    const [chart, setChart] = React.useState(null);
    const [initialZoomSet, setInitialZoomSet] = React.useState(false); // Tracks if we have set the initial zoom yet
    const [tooltipPrices, setTooltipPrices] = React.useState({});
    const [hovering, setHovering] = React.useState(false); // True if hovering a data series;
    const [candlestickSeries, setCandlestickSeries] = React.useState(null);
    const { active_period, candlesticks } = props;

    if (ref.current && !chart) {
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

    React.useEffect(() => {
        if(chart) {
            let series = chart.addCandlestickSeries({
                upColor: '#53b987',
                downColor: '#eb4d5c',
                borderDownColor: '#eb4d5c',
                borderUpColor: '#53b987',
                wickDownColor: '#eb4d5c',
                wickUpColor: '#53b987',
            });
            setCandlestickSeries(series);

            chart.subscribeCrosshairMove(function(param) {
                if (param.seriesPrices.size) {
                    setHovering(true);
                    setTooltipPrices(param.seriesPrices.get(series));
                } else {
                    setHovering(false);
                }
            })
        };
    }, [chart]);

    React.useEffect(() => {
        if (candlesticks.length && candlestickSeries) {
            candlestickSeries.setData(candlesticks);
            if (!hovering) {
                setTooltipPrices(candlesticks[candlesticks.length - 1]);
            }
        }

        if (!initialZoomSet && chart && chart.timeScale().getVisibleRange()) {
            let timeDiff = candlesticks[candlesticks.length -1]['time'] - candlesticks[candlesticks.length -2]['time'];
            chart.timeScale().setVisibleRange({
                from: candlesticks[candlesticks.length -1]['time'] - (timeDiff * 30), // Show 30 candles by default
                to: candlesticks[candlesticks.length -1]['time'],
            })
            setInitialZoomSet(true);
            setTooltipPrices(candlesticks[candlesticks.length - 1])
        }
    }, [candlesticks, candlestickSeries, chart, hovering, initialZoomSet]);

    function resizeChart() {
        if (chart) {
            chart.resize(0, 0);
            chart.resize(ref.current.clientWidth, ref.current.clientHeight);
        }
    }

    window.addEventListener('resize', () => resizeChart());

    resizeChart();

    return (
        <div id="chart" ref={ref}>
            <Tooltip title={active_period} prices={tooltipPrices} />
        </div>
    )
}

export default Chart;