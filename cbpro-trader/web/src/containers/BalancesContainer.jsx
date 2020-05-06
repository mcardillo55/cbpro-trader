import { connect } from 'react-redux'
import Balances from '../components/Balances'

const mapStateToProps = state => ({
    balances: state.sidebar.balances
})

export default connect(mapStateToProps)(Balances);