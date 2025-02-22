import React, { useState, useEffect } from "react";
import { Table, Button, Container } from "react-bootstrap";
import { fetchProducts, addToCart } from "../api";

const Products = ({ apiUrl, userId }) => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetchProducts(apiUrl).then(setProducts);
  }, [apiUrl]);

  return (
    <Container>
      <h2>Products ({products.length})</h2>
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
                <Button 
                  onClick={() => addToCart(apiUrl, userId, product.id)} 
                  disabled={product.stock <= 0}>
                  Add to Cart
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};

export default Products;
