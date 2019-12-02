import React, { Component } from 'react'
import Chart from './Chart'
import Details from './Details'

class ChartController extends Component {
    componentDidMount() {
        fetch("/periods/")
            .then(response => {
                return response.json()
            })
            .then(myJson => {
                myJson.map((period_name, idx) => {
                    (idx === 0) && this.props.changeActivePeriod(period_name);
                    return this.props.addPeriod(period_name);
                })
                
            })
    }

    render() {
        const { active_period, period_list, changeActivePeriod } = this.props;
        return (
            <div id="chart-controller">
                <Chart period_name={active_period} />
                <div id="sidebar">
                    <ul id="currency-list">
                        {period_list.map(period_name => {
                            return(
                                <li className={active_period === period_name ? "focused" : ""} onClick={() => {changeActivePeriod(period_name)}}>{period_name}</li>
                            )
                        })}
                    </ul>
                    <div id="secondary-section">
                        <div id="secondary-selector">
                            <button>Details</button>
                            <button>Flags</button>
                            <button>Orders</button>
                        </div>
                        <Details period_name={active_period}/>
                    </div>
                </div>
            </div>
        )
    }
}

export default ChartController