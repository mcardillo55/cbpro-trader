import React, { Component } from 'react'
import { connect } from 'react-redux'
import { addPeriod, changeActivePeriod, updateCandlesticks } from '../actions'
import ChartContainer from '../containers/ChartContainer'
import Details from '../components/Details'

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
              setInterval(() => {
                fetch("/periods/" + this.props.active_period)
                    .then(response => {
                        return response.json()
                    })
                    .then(myJson => {
                        this.props.updateCandlesticks(myJson)
                    })
              }, 1000)
            )
    }

    render() {
        const { active_period, period_list, changeActivePeriod } = this.props;
        return (
            <div id="chart-controller">
                <ChartContainer />
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

const mapStateToProps = state => ({
    period_list: state.period_list,
    active_period: state.active_period
  })
  
  const mapDispatchToProps = dispatch => ({
    addPeriod: period_name => dispatch(addPeriod(period_name)),
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
    updateCandlesticks: candlesticks => dispatch(updateCandlesticks(candlesticks))
  })

export default connect(mapStateToProps, mapDispatchToProps)(ChartController);