import React, { Component } from 'react'
import { connect } from 'react-redux'
import { addPeriod, changeActivePeriod, updateCandlesticks, updateIndicators, updateFlags } from '../actions'
import ChartContainer from '../containers/ChartContainer'
import SidebarContainer from '../containers/SidebarContainer'

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
            .then(
                setInterval(() => this.update(), 1000)
            )
    }

    update() {
        if (this.props.active_period) {
            fetch("/periods/" + this.props.active_period)
                .then(response => {
                    return response.json()
                })
                .then(myJson => {
                    this.props.updateCandlesticks(myJson)
                })
            switch(this.props.active_section) {
                case "details":
                    fetch("/indicators/" + this.props.active_period)
                        .then(response => {
                            return response.json()
                        })
                        .then(myJson => {
                            this.props.updateIndicators(myJson)
                        })
                    break;
                case "flags":
                    fetch("/flags/")
                        .then(response => {
                            return response.json()
                        })
                        .then(myJson => {
                            this.props.updateFlags(myJson)
                        })
                    break;
                default:
                    break;
            }
        }
    }

    render() {
        this.update();
        return (
            <div id="chart-controller">
                <ChartContainer />
                <SidebarContainer />
            </div>
        )
    }
}

const mapStateToProps = state => ({
    active_period: state.chart.active_period,
    active_section: state.sidebar.active_section
  })
  
const mapDispatchToProps = dispatch => ({
    addPeriod: period_name => dispatch(addPeriod(period_name)),
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
    updateCandlesticks: candlesticks => dispatch(updateCandlesticks(candlesticks)),
    updateIndicators: indicators => dispatch(updateIndicators(indicators)),
    updateFlags: flags => dispatch(updateFlags(flags))
})

export default connect(mapStateToProps, mapDispatchToProps)(ChartController);