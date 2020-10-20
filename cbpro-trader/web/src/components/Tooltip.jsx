import React from 'react';

function Tooltip (props) {
    return (
        <div id="tooltip">
            <div id="tooltip-title">{props.title}</div>
            <div id="tooltip-prices">O: {props.prices.open} H: {props.prices.high} L: {props.prices.low} C: {props.prices.close}</div>
        </div>
    )
}

export default Tooltip;