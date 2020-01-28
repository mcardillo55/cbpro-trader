import { connect } from 'react-redux'
import Flags from '../components/Flags'

const mapStateToProps = state => ({
    flags: state.sidebar.flags
})

export default connect(mapStateToProps)(Flags);