import React, { useState, useEffect } from "react";
import { Table, Button, Container } from "react-bootstrap";
import { fetchCart, removeFromCart } from "../api";

const Cart = ({ apiUrl, userId }) => {
  const [cart, setCart] = useState([]);

  useEffect(() => {
    refreshCart();
  }, [apiUrl, userId]);

  const refreshCart = async () => {
    const updatedCart = await fetchCart(apiUrl, userId);
    setCart([...updatedCart]); // Force state change
  };
  

  const handleRemove = async (productId) => {
    console.log("🗑️ Removing item from cart:", productId);
    
    const success = await removeFromCart(apiUrl, userId, productId);
    
    if (success) {
      console.log("✅ Removed! Refreshing cart...");
      refreshCart(); // Ensure database and UI stay in sync
    } else {
      console.error("❌ Failed to remove item from cart.");
    }
  };

  return (
    <Container>
      <h2>Cart ({cart.length})</h2>
      {cart.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Name</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {cart.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.quantity}</td>
                <td>${item.price}</td>
                <td>
                  <Button variant="danger" onClick={() => handleRemove(item.id)}>
                    Remove
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
};

export default Cart;
