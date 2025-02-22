const DNS_URL = "http://localhost:4000/getServer";

export const getApiUrl = async () => {
  try {
    const response = await fetch(DNS_URL);
    const data = await response.json();
    return `http://${data.server}`;
  } catch (error) {
    console.error("❌ Error fetching API URL:", error);
    return "http://localhost:3001"; // Fallback URL
  }
};

export const fetchProducts = async (apiUrl) => {
  try {
    const response = await fetch(`${apiUrl}/products`);
    return await response.json();
  } catch (error) {
    console.error("❌ Error fetching products:", error);
  }
};

export const fetchCart = async (apiUrl, userId) => {
    try {
      const response = await fetch(`${apiUrl}/cart/${userId}`, { cache: "no-store" });
      const data = await response.json();
  
      console.log("🛒 Updated Cart Data:", data);
      return data;
    } catch (error) {
      console.error("❌ Error fetching cart:", error);
      return [];
    }
  };
  

export const addToCart = async (apiUrl, userId, productId) => {
    try {
      const response = await fetch(`${apiUrl}/cart/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });
  
      const result = await response.json();
      console.log("🔄 API Response:", result);
  
      if (response.ok) {
        return true;
      } else {
        throw new Error("Failed to add item to cart");
      }
    } catch (error) {
      console.error("❌ Error adding to cart:", error);
      return false;
    }
  };
  

  export const removeFromCart = async (apiUrl, userId, productId) => {
    try {
      const response = await fetch(`${apiUrl}/cart/${userId}/item/${productId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
  
      const result = await response.json();
      console.log("🗑️ API Response (Remove from Cart):", result);
  
      return response.ok;
    } catch (error) {
      console.error("❌ Error removing from cart:", error);
      return false;
    }
  };
  
  

export const placeOrder = async (apiUrl, userId, cartItems) => {
  try {
    const response = await fetch(`${apiUrl}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, cart_items: cartItems }),
    });
    return await response.json();
  } catch (error) {
    console.error("❌ Error placing order:", error);
  }
};

export const fetchOrders = async (apiUrl, userId) => {
  try {
    const response = await fetch(`${apiUrl}/orders/${userId}`);
    return await response.json();
  } catch (error) {
    console.error("❌ Error fetching orders:", error);
  }
};
