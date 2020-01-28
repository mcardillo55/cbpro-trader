import React from 'react';
import DetailsContainer from '../containers/DetailsContainer'
import FlagsContainer from '../containers/FlagsContainer'

function Sidebar(props) {
    const { active_period, period_list, active_section, changeActiveSection, changeActivePeriod } = props;
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
                    <button className={active_section === "details" ? "active-button" : ""} onClick={() => {changeActiveSection("details")}}>Details</button>
                    <button className={active_section === "flags" ? "active-button" : ""} onClick={() => {changeActiveSection("flags")}}>Flags</button>
                    <button className={active_section === "orders" ? "active-button" : ""} onClick={() => {changeActiveSection("orders")}}>Orders</button>
                </div>
                {active_section === "details" && <DetailsContainer />}
                {active_section === "flags" && <FlagsContainer />}
                {active_section === "orders" && <p>Orders Section</p>}
            </div>
        </div>
    )
}

export default Sidebar;