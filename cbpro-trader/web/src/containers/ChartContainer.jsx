import { connect } from 'react-redux'
import Chart from '../components/Chart'

const mapStateToProps = state => ({
    active_period: state.chart.active_period,
    candlesticks: state.chart.candlesticks
})

export default connect(mapStateToProps)(Chart);