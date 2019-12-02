import { connect } from 'react-redux'
import Chart from '../components/Chart'

const mapStateToProps = state => ({
    active_period: state.active_period,
    candlesticks: state.candlesticks
})

export default connect(mapStateToProps)(Chart);