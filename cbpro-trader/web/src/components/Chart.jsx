import React, { Component } from 'react';
import { VictoryCandlestick, VictoryChart, VictoryAxis, VictoryLabel, VictoryTheme } from 'victory';

class Chart extends Component {
    constructor(props) {
        super(props);
        this.state = {candlesticks: []};
    }
    componentDidMount() {
        setInterval(() => {
            fetch("/periods/" + this.props.period_name)
                .then(response => {
                    return response.json()
                })
                .then(myJson => {
                    this.setState({candlesticks: myJson})
                })
        }, 1000)
    }

    render() {
        return (
            <div id="chart">
                <VictoryChart 
                    theme={VictoryTheme.material}
                    domainPadding={{ x: 15 }}
                    height={600}
                    width={1000}
                    scale={{ x: "time"}}
                >
                    <VictoryLabel text={this.props.period_name} x={480} y={15} style={{"font-weight": "bold", fill: "rgb(217, 217, 217)"}}/>
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

                    data={this.state.candlesticks.slice(this.state.candlesticks.length-50, this.state.candlesticks.length)}
                    x={(d) => Date.parse(d[0])}
                    open={3}
                    close={4}
                    high={2}
                    low={1} />
                </VictoryChart>
            </div>
        )
    }
};

export default Chart;