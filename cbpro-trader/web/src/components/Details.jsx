import React, { Component } from 'react';

class Details extends Component {
    constructor(props) {
        super(props);
        this.state = {details: {}};
    }
    componentDidMount() {
        setInterval(() => {
            fetch("/indicators/" + this.props.period_name)
                .then(response => {
                    return response.json()
                })
                .then(myJson => {
                    this.setState({details: myJson})
                })
        }, 1000)
    }

    render() {
        return(
            <div id="details">
                <div id="last-trade-label">Last Trade</div>
                <div id="last-trade">{this.state.details.close && this.state.details.close.toFixed(2)}</div>
                <div id="indicators">
                    {
                        Object.keys(this.state.details).map((indicator) => {
                            return(
                                <div class="indicator">
                                    <div class="indicator-title">{indicator.toUpperCase()}</div>
                                    <div class="indicator-data">{this.state.details[indicator]}</div>
                                </div>
                            )
                        })
                    }
                </div>
            </div>
        )
    }
};

export default Details;