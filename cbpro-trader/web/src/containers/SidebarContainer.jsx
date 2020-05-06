import { connect } from 'react-redux'
import { changeActivePeriod, changePrimarySection, changeSecondarySection } from '../actions'
import Sidebar from '../components/Sidebar'

const mapStateToProps = state => ({
    period_list: state.chart.period_list,
    active_period: state.chart.active_period,
    primary_section: state.sidebar.primary_section,
    secondary_section: state.sidebar.secondary_section
})

const mapDispatchToProps = dispatch => ({
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
    changePrimarySection: section_name => dispatch(changePrimarySection(section_name)),
    changeSecondarySection: section_name => dispatch(changeSecondarySection(section_name))
})

export default connect(mapStateToProps, mapDispatchToProps)(Sidebar);