import React from 'react';
import DetailsContainer from '../containers/DetailsContainer'
import FlagsContainer from '../containers/FlagsContainer'
import OrdersContainer from '../containers/OrdersContainer'
import BalancesContainer from '../containers/BalancesContainer';
import Config from '../components/Config';

function Sidebar(props) {
    const { active_period, period_list, primary_section, secondary_section, changePrimarySection, changeSecondarySection, changeActivePeriod } = props;
    
    let period_list_map = period_list.map(period_name => {
                                return(
                                    <li className={active_period === period_name ? "focused period" : "period"} 
                                        onClick={() => {changeActivePeriod(period_name)}}>{period_name}</li>
                                )
                            })

    return (
        <div id="sidebar">
            <div id="primary-section">
                <div id="primary-selector">
                    <button className={primary_section === "periods" ? "active-button" : ""} onClick={() => {changePrimarySection("periods")}}>Periods</button>
                    <button className={primary_section === "balances" ? "active-button" : ""} onClick={() => {changePrimarySection("balances")}}>Balances</button>
                    <button className={primary_section === "config" ? "active-button" : ""} onClick={() => {changePrimarySection("config")}}>Config</button>
                </div>
                <div id="primary-details">
                    { primary_section === "periods" &&  period_list_map }
                    { primary_section === "balances" && <BalancesContainer /> }
                    { primary_section === "config" && <Config /> }
                </div>
            </div>
            <div id="secondary-section">
                <div id="secondary-selector">
                    <button className={secondary_section === "details" ? "active-button" : ""} onClick={() => {changeSecondarySection("details")}}>Details</button>
                    <button className={secondary_section === "flags" ? "active-button" : ""} onClick={() => {changeSecondarySection("flags")}}>Flags</button>
                    <button className={secondary_section === "orders" ? "active-button" : ""} onClick={() => {changeSecondarySection("orders")}}>Orders</button>
                </div>
                <div id="secondary-details">
                    {secondary_section === "details" && <DetailsContainer />}
                    {secondary_section === "flags" && <FlagsContainer />}
                    {secondary_section === "orders" && <OrdersContainer />}
                </div>
            </div>
        </div>
    )
}

export default Sidebar;