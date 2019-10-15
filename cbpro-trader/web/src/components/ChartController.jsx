import React, { Component } from 'react';
import Chart from './Chart';
import Details from './Details';

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
                <Chart period_name={this.state.active_period} />
                <div id="sidebar">
                    <ul id="currency-list">
                        {this.state.period_list.map(period_name => {
                            return(
                                <li className={this.state.active_period === period_name ? "focused" : ""} onClick={() => this.setState({active_period: period_name})}>{period_name}</li>
                            )
                        })}
                    </ul>
                    <Details period_name={this.state.active_period}/>
                </div>
            </div>
        )
    }
};

export default ChartController;