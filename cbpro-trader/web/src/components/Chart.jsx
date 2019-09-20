import React, { Component } from 'react';
import { VictoryCandlestick, VictoryChart, VictoryAxis, VictoryTheme } from 'victory';

class Chart extends Component {
    constructor(props) {
        super(props);
        this.state = {periods: []};
    }
    componentDidMount() {
        setInterval(() => {
            fetch("/periods/")
                .then(response => {
                    return response.json()
                })
                .then(myJson => {
                    this.setState({periods: myJson})
                })
            }, 1000);
    }

    render() {
        return (
            <VictoryChart 
                theme={VictoryTheme.material}
                domainPadding={{ x: 10 }}
                height={200}
                width={300}
                scale={{ x: "time"}}
            >
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
                    tickLabels: {fontSize: 2}
                }}
            />
            <VictoryAxis 
                style={{
                    tickLabels: {fontSize: 2}
                }}
                dependentAxis
            />
               {
                this.state.periods.map(period => {
                    return (
                    <VictoryCandlestick
                    candleColors={{ positive: "green", negative: "red" }}
                    data={period.candlesticks.slice(period.candlesticks.length-50, period.candlesticks.length)}
                    x={(d) => Date.parse(d[0])}
                    open={3}
                    close={4}
                    high={2}
                    low={1} />
                    )
                })
            }
            </VictoryChart>
        )
    }
};

export default Chart;