import React, { useState, useEffect } from "react";
import { Table, Container } from "react-bootstrap";
import { fetchOrders } from "../api";

const Orders = ({ apiUrl, userId }) => {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetchOrders(apiUrl, userId).then(setOrders);
  }, [apiUrl]);

  return (
    <Container>
      <h2>Your Orders</h2>
      {orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Total Price</th>
              <th>Status</th>
              <th>Created At</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td>{order.id}</td>
                <td>${order.total_price.toFixed(2)}</td>
                <td>{order.status}</td>
                <td>{new Date(order.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
};

export default Orders;
