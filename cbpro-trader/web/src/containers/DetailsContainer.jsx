import { connect } from 'react-redux'
import Details from '../components/Details'

const mapStateToProps = state => ({
    indicators: state.indicators
})

export default connect(mapStateToProps)(Details);