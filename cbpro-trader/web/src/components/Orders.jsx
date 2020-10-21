import React from 'react';

function Orders(props) {
    const { orders } = props;
    return(
        <div id="orders" className="sidebar-section">
            <h2 className="first-h2">Orders</h2>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Side</th>
                        <th>Size</th>
                        <th>Price</th>
                        <th>Filled</th>
                        <th>Fee</th>
                    </tr>
                </thead>
                <tbody>
            {
                orders['orders'].map((order, idx) => {
                    return(
                        <tr key={idx}>
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
                </tbody>
            </table>
            <h2>Fills</h2>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Side</th>
                        <th>Size</th>
                        <th>Price</th>
                        <th>Fee</th>

                    </tr>
                </thead>
                <tbody>
            {
                orders['fills'].map((fill, idx) => {
                    return(
                        <tr key={idx}>
                            <td>{fill.product_id}</td>
                            <td>{fill.side.toUpperCase()}</td>
                            <td>{fill.size}</td>
                            <td>{parseFloat(fill.price).toFixed(2)}</td>
                            <td>{parseFloat(fill.fee).toFixed(8)}</td>
                        </tr>
                    )
                })
            }
                </tbody>
            </table>
        </div>
    )
}

export default Orders;