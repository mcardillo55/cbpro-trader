import React from 'react';
import DetailsContainer from '../containers/DetailsContainer'

function Chart(props) {
    const { active_period, period_list, changeActivePeriod } = props;
    return (
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
                <DetailsContainer />
            </div>
        </div>
    )
}

export default Chart;