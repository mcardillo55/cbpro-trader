import React, { Component } from 'react'

class Config extends Component {
    constructor(){
        super();
        this.state = {"config": {"periods": []}}
    }
    
    componentDidMount() {
        fetch('/config/')
        .then(response => response.json())
        .then(myJson => this.setState({"config": myJson}))
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
    createInput(value) {
        let type = this.parseType(value)
        let checked = type === "checkbox" && value ? "checked" : ""
        return <input type={type} checked={checked} value={value} />
    }

    render() {
        let periods_list = 
            this.state.config["periods"].map((period) => {
                return(
                    Object.keys(period).map((period_value) => {
                        return(
                            <div>
                                <label>
                                    {period_value}:
                                </label>
                                {this.createInput(period[period_value])}
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
                            {this.createInput(this.state.config[config])}
                        </div>
                    )  
                }
            });
        return (
            <form>
                {config_list}
            </form>
        );
    }
}

export default Config;