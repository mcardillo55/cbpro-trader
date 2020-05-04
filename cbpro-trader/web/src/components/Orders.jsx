import React from 'react';

function Orders(props) {
    const { orders } = props;
    return(
        <div id="orders">
            <h2>Orders</h2>
            {
                orders['orders'].map((order) => {
                    return(
                        
                        <div class="order">
                            {order.side} {order.size} {order.filled_size} {order.fill_fees} {order.price} 
                        </div>
                    )
                })
            }
            <h2>Fills</h2>
            {
                orders['fills'].map((fill) => {
                    return(
                        
                        <div class="fill">
                            {fill.product_id} {fill.side} {fill.size} {fill.fee} {fill.price} 
                        </div>
                    )
                })
            }
        </div>
    )
}

export default Orders;