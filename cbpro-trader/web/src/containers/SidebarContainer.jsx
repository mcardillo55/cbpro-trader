import React, { Component } from 'react'
import { connect } from 'react-redux'
import { changeActivePeriod } from '../actions'
import Sidebar from '../components/Sidebar'

const mapStateToProps = state => ({
    period_list: state.chart.period_list,
    active_period: state.chart.active_period
})

const mapDispatchToProps = dispatch => ({
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
})

export default connect(mapStateToProps, mapDispatchToProps)(Sidebar);