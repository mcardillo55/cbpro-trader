import React from 'react';

function Orders(props) {
    const { orders } = props;
    return(
        <div id="orders" className="sidebar-section">
            <h2 className="first-h2">Orders</h2>
            <table>
                <tr>
                    <th>Product</th>
                    <th>Side</th>
                    <th>Size</th>
                    <th>Price</th>
                    <th>Filled</th>
                    <th>Fee</th>
                </tr>
            {
                orders['orders'].map((order) => {
                    return(
                        <tr>
                            <td>{order.product_id}</td>
                            <td>{order.side.toUpperCase()}</td>
                            <td>{order.size}</td>
                            <td>{parseFloat(order.price).toFixed(2)}</td>
                            <td>{order.filled_size}</td>
                            <td>{parseFloat(order.fill_fees).toFixed(8)}</td>
                        </tr>
                    )
                })
            }
            </table>
            <h2>Fills</h2>
            <table>
                <tr>
                    <th>Product</th>
                    <th>Side</th>
                    <th>Size</th>
                    <th>Price</th>
                    <th>Fee</th>

                </tr>  
            {
                orders['fills'].map((fill) => {
                    return(
                        <tr>
                            <td>{fill.product_id}</td>
                            <td>{fill.side.toUpperCase()}</td>
                            <td>{fill.size}</td>
                            <td>{parseFloat(fill.price).toFixed(2)}</td>
                            <td>{parseFloat(fill.fee).toFixed(8)}</td>
                        </tr>
                    )
                })
            }
            </table>
        </div>
    )
}

export default Orders;