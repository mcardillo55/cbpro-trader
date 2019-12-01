import { connect } from 'react-redux'
import { addPeriod, changeActivePeriod } from '../actions'
import ChartController from '../components/ChartController'

const mapStateToProps = state => ({
    period_list: state.period_list,
    active_period: state.active_period
  })
  
  const mapDispatchToProps = dispatch => ({
    addPeriod: period_name => dispatch(addPeriod(period_name)),
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name))
  })

export default connect(mapStateToProps, mapDispatchToProps)(ChartController);