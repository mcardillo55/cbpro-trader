import React, { Component } from 'react'
import { connect } from 'react-redux'
import { changeActivePeriod } from '../actions'
import DetailsContainer from '../containers/DetailsContainer'

class SidebarContainer extends Component {
    render() {
        const { period_list, active_period, changeActivePeriod } = this.props;
        return(
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
}
const mapStateToProps = state => ({
    period_list: state.chart.period_list,
    active_period: state.chart.active_period
})

const mapDispatchToProps = dispatch => ({
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
})

export default connect(mapStateToProps, mapDispatchToProps)(SidebarContainer);