import React from 'react';

function Flags(props) {
    const { flags } = props;
    return(
        <div id="flags" className="sidebar-section">
            <h2 className="first-h2">Flags</h2>
            {
                Object.keys(flags).map((flag, idx) => {
                    return(      
                        <div key={idx} className="flag">
                            <span className="flag-title">{ flag.toUpperCase() }:</span> { flags[flag].toUpperCase() }
                        </div>
                    )
                })
            }
        </div>
    )
}

export default Flags;