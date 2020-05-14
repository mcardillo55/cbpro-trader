import React, { Component } from 'react'
import { connect } from 'react-redux'
import { addPeriod, changeActivePeriod, clearPeriods } from '../actions'

class Config extends Component {
    constructor(){
        super();
        this.SERVER = process.env.REACT_APP_SERVER || '';
        this.state = {"config": {"periods": []}}
        this.handleConfigChange = this.handleConfigChange.bind(this)
        this.handlePeriodChange = this.handlePeriodChange.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
    }
    
    componentDidMount() {
        fetch(this.SERVER + '/config/')
        .then(response => response.json())
        .then(myJson => this.setState({"config": myJson}))
    }

    handleConfigChange(event) {
        this.setState({
                        config: {...this.state.config,
                                [event.target.name]: this.parseEventData(event)
                                }
                        })
    }

    handlePeriodChange(event) {
        let idx = event.target.name.split("+")[0]
        let name = event.target.name.split("+")[1]
        let periods = [...this.state.config.periods]
        let period = {...periods[idx],
                      [name]: this.parseEventData(event)}
        periods[idx] = period
        this.setState({
                        config: {...this.state.config,
                                periods: periods
                                }
                        })
    }

    handleSubmit(event){
        event.preventDefault()
        fetch(this.SERVER + '/config/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(this.state.config)
        })
        .then(() => {
            this.props.clearPeriods()
            fetch(this.SERVER + "/periods/")
            .then(response => {
                return response.json()
            })
            .then(myJson => {
                myJson.map((period_name, idx) => {
                    (idx === 0) && this.props.changeActivePeriod(period_name);
                    return this.props.addPeriod(period_name);
                })
            })
        })
    }

    parseEventData(event) {
        switch (event.target.type) {
            case "text":
                return event.target.value
            case "number":
                return parseFloat(event.target.value)
            case "checkbox":
                return event.target.checked
            default:
                return "text"
        } 
    }

    parseType(data) {
        switch (typeof(data)) {
            case "text":
                return "text"
            case "number":
                return "number"
            case "boolean":
                return "checkbox"
            default:
                return "text"
        } 
    }
    createInput(label, value, period) {
        let type = this.parseType(value)
        let checked = type === "checkbox" && value ? "checked" : ""
        return <input type={type} 
                      checked={checked}
                      value={value} 
                      name={label} 
                      onChange={period ? this.handlePeriodChange : this.handleConfigChange}/>
    }

    render() {
        let periods_list = 
            this.state.config["periods"].map((period, idx) => {
                return(
                    Object.keys(period).map((period_value) => {
                        return(
                            <div>
                                <label>
                                    {period_value}:
                                </label>
                                {this.createInput(idx + "+" + period_value, period[period_value], true)}
                            </div>
                        )
                    })
                )
            });
        let config_list = 
            Object.keys(this.state.config).map((config) => {
                if (config === "periods") {
                    return(
                        <div>
                            Periods:
                                {periods_list}
                        </div>
                    )
                } else {
                    return (
                        <div>
                            <label>
                                {config}:
                            </label>
                            {this.createInput(config, this.state.config[config], false)}
                        </div>
                    )  
                }
            });
        return (
            <form id="config">
                {config_list}
                <input type="submit" value="Save and Restart" onClick={this.handleSubmit}/>
            </form>
        );
    }
}

const mapDispatchToProps = dispatch => ({
    addPeriod: period_name => dispatch(addPeriod(period_name)),
    changeActivePeriod: period_name => dispatch(changeActivePeriod(period_name)),
    clearPeriods: () => dispatch(clearPeriods())
})

export default connect(null, mapDispatchToProps)(Config);