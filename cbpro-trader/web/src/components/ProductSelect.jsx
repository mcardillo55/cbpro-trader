import React, { Component } from 'react'

class ProductSelect extends Component {
    constructor(props){
        super(props)
        this.SERVER = process.env.REACT_APP_SERVER || ''
        this.state = {products: []}
    }
    componentDidMount() {
        fetch(this.SERVER + '/products/')
        .then(response => response.json())
        .then(myJson => this.setState({products: myJson}))
    }
    render() {
        let options = this.state.products.map(option => {
            return <option value={option} onChange={this.handleChange} selected={option === this.props.selected ? true : ""}>{option}</option>
        })
        return (
            <select name={this.props.name} onChange={this.props.onChange} value={this.state.selected}>
                {options}
            </select>
        )
    }
}

export default ProductSelect;