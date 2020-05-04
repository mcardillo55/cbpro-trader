import React from 'react';

function Details(props) {
    const { indicators } = props;
    return(
        <div id="details" className="sidebar-section">
            <div id="last-trade-label">Last Trade</div>
            <div id="last-trade">{indicators.close && indicators.close.toFixed(2)}</div>
            <div id="indicators">
                {
                    Object.keys(indicators).map((indicator) => {
                        return(
                            <div class="indicator">
                                <div class="indicator-title">{indicator.toUpperCase()}</div>
                                <div class="indicator-data">{indicators[indicator]}</div>
                            </div>
                        )
                    })
                }
            </div>
        </div>
    )
}

export default Details;