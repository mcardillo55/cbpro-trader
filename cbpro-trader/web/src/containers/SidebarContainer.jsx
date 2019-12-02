import { connect } from 'react-redux'
import { changeActivePeriod, changeActiveSection } from '../actions'
import Sidebar from '../components/Sidebar'

const mapStateToProps = state => ({
    period_list: state.chart.period_list,
    active_period: state.chart.active_period,
    active_section: state.sidebar.active_section
})

const mapDispatchToProps = dispatch => ({
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
    changeActiveSection: section_name => dispatch(changeActiveSection(section_name))
})

export default connect(mapStateToProps, mapDispatchToProps)(Sidebar);