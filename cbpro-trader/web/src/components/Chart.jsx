import React, { Component } from 'react';
import { VictoryCandlestick, VictoryChart, VictoryAxis, VictoryLabel, VictoryTheme } from 'victory';

function Chart (props) {
    const { active_period, candlesticks } = props;
    return (
        <div id="chart">
            <VictoryChart 
                theme={VictoryTheme.material}
                domainPadding={{ x: 15 }}
                height={600}
                width={1000}
                scale={{ x: "time"}}
            >
                <VictoryLabel text={active_period} x={20} y={20} style={{
                                                                                    fontWeight: "bold",
                                                                                    fontSize: 20,
                                                                                    fill: "rgb(217, 217, 217)"
                                                                                    }}/>
                <VictoryAxis 
                    tickFormat={(t) => `${t.toLocaleString(undefined, {year: "2-digit",
                                                            month: "numeric",
                                                            day: "numeric",
                                                            hour: "numeric",
                                                            minute: "numeric",
                                                            hourCycle: "h24"
                                                            }).replace(',', '\n')}`}
                    tickCount={25}
                    style={{
                        tickLabels: {
                            fill: "rgb(217, 217, 217)"
                        }
                    }}
                />
                <VictoryAxis 
                    dependentAxis
                    style={{
                        tickLabels: {
                            fill: "rgb(217, 217, 217)"
                        }
                    }}
                />
                <VictoryCandlestick
                candleColors={{ positive: "#53b987", negative: "#eb4d5c" }}

                data={candlesticks.slice(candlesticks.length-50, candlesticks.length)}
                x={(d) => Date.parse(d[0])}
                open={3}
                close={4}
                high={2}
                low={1} />
            </VictoryChart>
        </div>
    )
}

export default Chart;