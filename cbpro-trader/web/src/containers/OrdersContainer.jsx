import { connect } from 'react-redux'
import Orders from '../components/Orders'

const mapStateToProps = state => ({
    orders: state.sidebar.orders
})

export default connect(mapStateToProps)(Orders);