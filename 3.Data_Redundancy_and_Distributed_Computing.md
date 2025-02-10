# Data Redundancy and Distributed Computing Workshop

This workshop is structured into two principal sections, focusing initially on the distinctions and connections between decentralized computing and distributed computing, shedding light on their individual characteristics and areas of application.

### Overview

**Distributed Computing** is a paradigm in which the elements of a software system are dispersed across multiple computers to enhance efficiency and performance. Its defining feature is the pursuit of a collective objective by allocating tasks among several computers. Despite this dispersion, these systems may still operate under a degree of central oversight, necessitating a certain level of coordination and centralization for functions such as job scheduling and resource allocation.

**Decentralized Computing** extends the distributed computing model by eliminating the central governance element. In such systems, each node or computer functions independently, with decision-making distributed across individual nodes rather than centralized. This framework is often linked with blockchain technology, characterized by each network participant holding a ledger copy, enabling independent transaction validation.

### Practical Exercise: From Local to Decentralized Computation

Participants should form groups of 3 to 5 and select a simple dataset, such as Iris, Housing Market, or Titanic, for the following activities:

**Q1:** Develop diverse predictive models targeting the selected dataset. Each group member should create a distinct model.

- Evaluate the accuracy and performance of your model.
- Adapt your model for API access. This API should include a GET `predict` route that accepts model arguments and returns a prediction.
- Determine a standardized API response format within your group.

**Q2:** Generate a consensus prediction by averaging outputs from the group's models, using tools like ngrok for inter-computer connectivity. Assess the performance of this aggregated meta-model.

This stage illustrates the creation of a distributed prediction system in a trusted environment. The next step involves opening the model to external contributions, which may come from both benign and malicious actors.

### Introducing Consensus with Slashing Mechanism

**Q4:** Introduce a weighting system to refine the meta-model's predictions. Weights, ranging from 0 to 1, are adjusted with each prediction batch to reflect the accuracy of individual models relative to the group consensus.

**Q5:** Implement a proof-of-stake consensus mechanism with a slashing protocol. Models must make an initial deposit (e.g., 1000 euros) upon registration to participate. This deposit serves as a security measure, ensuring participants' commitment to the network's integrity.

- Implement penalties (slashing) for actions that undermine network accuracy or trustworthiness. For example, consistently inaccurate predictions may result in a loss of deposit.
- This protocol discourages adverse behaviors while encouraging contributions of accurate, reliable predictions.
- Adjust model weights based on performance and penalties, promoting a merit-based system that rewards accuracy and penalizes dishonesty or inaccuracy.

Incorporating a slashing mechanism enhances the network's reliability and accountability, ensuring that contributions are both accurate and made in good faith, thus maintaining the integrity and effectiveness of the decentralized prediction system.

To simplify the implementation asume that balance and slashing are done locally.
Create a Json Database were you track model balance.


## B - E-commerce - Importance of redundancy
###  Objectives
Understand the principles of service and data redundancies, its importance in system reliability and data integrity

###  Exercice - Simple Hello World Server

Q1 - Create a simple hello world server

Q2 - Create a DNS registry. This registry must be an express server that will have a getServer route. Route must repond the url of the server.

For exemple if your server run on port 3001, the response of getServer must me :
```json
{"code":200, "server":"localhost:3001"}
```

###  Exercice - Simple e-commerce

Now let's create the following e-commerce API:

**Note:** Removing the registration and login routes simplifies the workshop by focusing on the core functionalities of product and order management in the e-commerce platform. Below is the revised "cahier des charges" for the different routes, excluding user registration and login functionalities:

####  1. Products Routes

#####  GET /products
- **Description**: Retrieves a list of all products available in the store.
- **Request Body**: None.
- **Query Parameters**: Optional filters such as `category` to filter products by their category, and `inStock` to filter products based on their stock availability.
- **Response**: A JSON array of products, each containing details like name, description, price, and stock status.

#####  GET /products/:id
- **Description**: Fetches detailed information about a specific product identified by its ID.
- **Request Body**: None.
- **Response**: A JSON object containing detailed information of the product, including name, description, price, category, and stock status.

#####  POST /products
- **Description**: Adds a new product to the store.
- **Request Body**: JSON object containing product information such as name, description, price, category, and stock status.
- **Response**: A JSON object of the created product, including all details provided plus a unique identifier for the product.

#####  PUT /products/:id
- **Description**: Updates the details of an existing product.
- **Request Body**: JSON object with the product's updated information. Only fields to be updated need to be included.
- **Response**: The updated product details as a JSON object.

#####  DELETE /products/:id
- **Description**: Removes a product from the store by its ID.
- **Request Body**: None.
- **Response**: A confirmation message indicating successful deletion of the product.

####  2. Orders Routes

#####  POST /orders
- **Description**: Creates a new order with selected products.
- **Request Body**: JSON object containing an array of product IDs and their quantities, and optionally, user information if the system tracks orders per user without authentication.
- **Response**: Detailed information of the created order, including a unique order ID, list of products ordered with quantities, total price, and order status.

#####  GET /orders/:userId
- **Description**: Retrieves all orders placed by a specific user, identified by a user ID.
- **Request Body**: None.
- **Response**: An array of orders with detailed information about each order including order ID, products ordered, quantities, total price, and status.

####  3. Cart Routes

#####  POST /cart/:userId
- **Description**: Adds a product to the user's shopping cart.
- **Request Body**: JSON object containing the product ID and quantity.
- **Response**: Updated contents of the cart, including product details and total price.

#####  GET /cart/:userId
- **Description**: Retrieves the current state of a user's shopping cart.
- **Request Body**: None.
- **Response**: A JSON object listing the products in the cart, their quantities, and the total price.

#####  DELETE /cart/:userId/item/:productId
- **Description**: Removes a specific product from the user's shopping cart.
- **Request Body**: None.
- **Response**: The updated contents of the cart after removal of the specified product.

The provided text is mostly clear and informative, but there are some grammatical and spelling errors, as well as a few areas that could benefit from clarification or minor adjustments for accuracy and coherence. Here's a corrected version:

---

#### General Considerations

- **Validation and Error Handling**: Implement validation for all inputs to ensure data integrity and provide meaningful error messages for any incorrect inputs or operations that cannot be completed.
- **Data Format**: All responses should be in JSON format for easy parsing and integration with frontend systems.
- **Statelessness**: Ensure the API is stateless to simplify scaling and enhance reliability. This is especially important since user authentication is not being implemented.

Q3 - In order to implement the different routes, create a database to store the various fields. You can choose from: JSON-based DB, SQL, PostgreSQL, MongoDB, etc. Please note that this workshop will involve 2 different implementations, so use tools that you are comfortable using.

Q4 - Modify the server implementation to match API requirements.

Q5 - Create a simple front-end to interact with the server. Please note that style is not the priority here. You can use tools like Bootstrap or Ant Design if you want. Just don't spend too much time on this task.

Q6 - Simulate an issue/a stop of the API Server. What would be the result for the e-commerce user?

Fix it.
<details>
    <summary>💡 hint ?</summary>
    Modify the DNS.
</details>

Now imagine the e-commerce does 1000 orders/day, and the same inaccessibility occurs, but now not on the server but on the database. Let's imagine that your database is near a river and there is a flood, or there is a fire at our database data center. It will be painful, right? Let's see how to prevent this kind of issue.

#### Synchronous Mirroring

Synchronous mirroring, a cornerstone of high availability architectures, ensures real-time data availability across two (or in some cases three) storage systems – usually within the same site or across metro-clusters. When a write operation occurs, the system dispatches the data not only to the primary storage device but also, concurrently, to a mirror (or secondary) storage device. Thus, data redundancy is maintained constantly, ensuring a one-to-one data match across both storage systems.

The write operation is considered complete only after data is successfully stored in both the primary and mirrored storages. This establishes a consistent data state across devices, ensuring zero Recovery Point Objective (RPO) and Recovery Time Objective (RTO). Underneath this functionality lies a series of protocols and communication methodologies ensuring real-time data transfer, synchronization checks, failover, and failback operations. This also necessitates robust network infrastructures, often leveraging fiber channel or high-speed Ethernet, to mitigate latency.

Q7 - Modify the implementation to use synchronous mirroring. **Please copy your current file into a `Basic_Implementation` folder and make the following modifications in a new folder named `Synchronous_Mirroring`.**

#### Asynchronous Replication

Asynchronous replication ensures redundancy by periodically copying data from the primary to a secondary location – usually across long distances over a WAN connection. A key application of this is in disaster recovery. While the primary storage first acknowledges the write operation, data replication to the secondary storage might have a slight delay. Hence, it is asynchronous in nature. But, over time, the secondary storage is synced with the primary one, ensuring that a redundant copy is available (even if it might be slightly outdated compared to the primary copy).

Asynchronous replication employs a queue or buffer system. Once the primary storage acknowledges the write, the data is queued for replication. Advanced systems may implement algorithms to batch data, minimize network chatter, or prioritize data sequences. Change logs may be utilized to keep track of data states at specific intervals, allowing for periodic synchronization with secondary storage. This approach is especially prevalent in geographically dispersed disaster recovery architectures, where data is asynchronously replicated to remote sites.

Q8 - Adapt the implementation to use asynchronous replication. Do the implementation in a new folder named `Asynchronous-Replication`.

---

This version corrects spelling mistakes (e.g., "postgress" to "PostgreSQL", "inderact" to "interact"), clarifies instructions, and makes minor grammatical adjustments for readability.
