import React from 'react';

function Orders(props) {
    const { orders } = props;
    return(
        <div id="orders">
            {
                orders.map((order) => {
                    return(
                        
                        <div class="order">
                            {order.side} {order.size} {order.filled_size} {order.fill_fees} {order.price} 
                        </div>
                    )
                })
            }
        </div>
    )
}

export default Orders;