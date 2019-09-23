import React, { Component } from 'react';
import { VictoryCandlestick, VictoryChart, VictoryAxis, VictoryTheme } from 'victory';

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
            <VictoryCandlestick
            candleColors={{ positive: "green", negative: "red" }}
            data={this.state.candlesticks.slice(this.state.candlesticks.length-50, this.state.candlesticks.length)}
            x={(d) => Date.parse(d[0])}
            open={3}
            close={4}
            high={2}
            low={1} />
            </VictoryChart>
        )
    }
};

export default Chart;