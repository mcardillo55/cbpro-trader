import React, { Component } from 'react';
import Chart from './Chart';

class ChartController extends Component {
    constructor(props) {
        super(props);
        this.state = {period_list: [], active_period: undefined};
    }
    componentDidMount() {
        fetch("/periods/")
            .then(response => {
                return response.json()
            })
            .then(myJson => {
                this.setState({period_list: myJson, active_period: myJson[0]})
            })
    }

    render() {
        return (
            <div id="chart-controller">
                <ul id="currency-list">
                    {this.state.period_list.map(period_name => {
                        return(
                            <li onClick={() => this.setState({active_period: period_name})}>{period_name}</li>
                        )
                    })}
                </ul>
                <Chart period_name={this.state.active_period} />
            </div>
        )
    }
};

export default ChartController;