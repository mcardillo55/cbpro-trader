import React, { Component } from 'react'

class SelectAvailable extends Component {
    constructor(props){
        super(props)
        this.SERVER = process.env.REACT_APP_SERVER || ''
        this.state = {options: []}
    }
    componentDidMount() {
        if (this.props.url) {
            fetch(this.SERVER + this.props.url)
            .then(response => response.json())
            .then(myJson => this.setState({options: myJson}))
        } else if (this.props.options) {
            this.setState({options: this.props.options})
        }
    }
    render() {
        let options = this.state.options.map(option => {
            return <option value={option} onChange={this.handleChange} selected={option === this.props.selected ? true : ""}>{option}</option>
        })
        return (
            <select name={this.props.name} onChange={this.props.onChange} value={this.state.selected}>
                {options}
            </select>
        )
    }
}

export default SelectAvailable;