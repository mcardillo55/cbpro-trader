import React from 'react';

function Balances(props) {
    const { balances } = props;
    return(
        <div id="balances" className="sidebar-section">
            {
                Object.keys(balances).map((currency) => {
                    return(
                        <div class="balances">
                            <span className="currency">{ currency.toUpperCase() }:</span> { balances[currency] }
                        </div>
                    )
                })
            }
        </div>
    )
}

export default Balances;