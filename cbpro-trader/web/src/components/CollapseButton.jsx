import React from 'react';

function CollapseButton(props) {
    const buttonDirection = props.collapsed ? "<" : ">"
    return (
        <div id="collapse-button" onClick={props.onClick}>
            {buttonDirection}
        </div>
    )
}

export default CollapseButton;