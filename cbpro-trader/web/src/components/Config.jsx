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
                                <input type="text" value={period[period_value].toString()} />
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
                            <input type="text" value={this.state.config[config].toString()} />
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