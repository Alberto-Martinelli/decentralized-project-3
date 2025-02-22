import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Container, Button } from "react-bootstrap";
import Products from "./components/Products";
import Cart from "./components/Cart";
import Orders from "./components/Orders";
import { getApiUrl, placeOrder } from "./api";

const App = () => {
  const userId = 1;
  const [apiUrl, setApiUrl] = useState("http://localhost:3001");
  const [view, setView] = useState("products");

  useEffect(() => {
    getApiUrl().then(setApiUrl);
  }, []);

  return (
    <Container>
      <h1>E-Commerce Web App</h1>
      <p>API URL: {apiUrl}</p>
      <Button onClick={() => setView("products")}>Products</Button>
      <Button onClick={() => setView("cart")}>Cart</Button>
      <Button onClick={() => setView("orders")}>Orders</Button>

      {view === "products" && <Products apiUrl={apiUrl} userId={userId} />}
      {view === "cart" && <Cart apiUrl={apiUrl} userId={userId} />}
      {view === "orders" && <Orders apiUrl={apiUrl} userId={userId} />}
    </Container>
  );
};

export default App;
