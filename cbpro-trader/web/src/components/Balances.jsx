import React from 'react';

function Balances(props) {
    const { balances } = props;
    return(
        <ul id="balances" className="sidebar-section">
            {
                Object.keys(balances).map((currency) => {
                    return(
                        <li className="currency"><span className="currency">{ currency.toUpperCase() }</span>: { balances[currency] }</li>
                    )
                })
            }
        </ul>
    )
}

export default Balances;