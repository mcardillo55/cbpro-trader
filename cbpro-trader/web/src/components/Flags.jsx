import React from 'react';

function Flags(props) {
    const { flags } = props;
    return(
        <div id="flags">
            {
                Object.keys(flags).map((flag) => {
                    return(
                        
                        <div class="product">
                            <div class="product_name">{flag.toUpperCase()}</div>
                            <div class="flag">{flags[flag]}</div>
                        </div>
                    )
                })
            }
        </div>
    )
}

export default Flags;