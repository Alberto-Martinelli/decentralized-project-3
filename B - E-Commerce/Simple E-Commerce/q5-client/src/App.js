import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Container, Button, Table } from "react-bootstrap";

const DNS_URL = "http://localhost:4000/getServer";

function App() {
  console.log("✅ React App is Mounting...");

  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [apiUrl, setApiUrl] = useState("http://localhost:3001"); // Hardcoded for testing
  const userId = 1;

  useEffect(() => {
    console.log("Fetching API URL...");
    fetch(DNS_URL)
      .then((res) => res.json())
      .then((data) => {
        console.log("✅ Fetched API URL:", data.server);
        setApiUrl(`http://${data.server}`);
        fetchProducts(`http://${data.server}`);
        fetchCart(`http://${data.server}`);
      })
      .catch((err) => console.error("❌ Error fetching API URL:", err));
  }, []);

  const fetchProducts = async (url) => {
    try {
      console.log("Fetching products from:", url);
      const response = await fetch(`${url}/products`);
      const data = await response.json();
      console.log("✅ Fetched Products:", data);
      setProducts(data);
    } catch (error) {
      console.error("❌ Error fetching products:", error);
    }
  };

  const fetchCart = async (url) => {
    try {
      console.log("Fetching cart from:", url);
      const response = await fetch(`${url}/cart/${userId}`);
      const data = await response.json();
      console.log("✅ Fetched Cart:", data);
      setCart(data);
    } catch (error) {
      console.error("❌ Error fetching cart:", error);
    }
  };

  return (
    <Container className="mt-4">
      <h1 style={{ color: "green" }}>React App Loaded</h1>
      <p>API URL: {apiUrl}</p>

      <h2>Products ({products.length})</h2>
      {products.length > 0 ? (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.description}</td>
                <td>${product.price}</td>
                <td>{product.stock}</td>
                <td>
                  <Button onClick={() => console.log("Adding to cart:", product.id)} disabled={product.stock <= 0}>
                    Add to Cart
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      ) : (
        <p>No products available.</p>
      )}

      <h2>Cart ({cart.length})</h2>
      {cart.length === 0 ? (
        <p>Your cart is empty</p>
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
                  <Button variant="danger" onClick={() => console.log("Removing from cart:", item.id)}>
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
}

export default App;