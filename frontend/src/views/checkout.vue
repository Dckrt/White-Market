<template>
  <div>

    <!-- NAV -->
    <header class="nav">

  <h1 class="logo">White Market</h1>

  <div class="nav-center">
    <button @click="$router.push('/')">Home</button>
    <button @click="$router.push('/browse')">Browse</button>

    <!-- SELLER ONLY -->
    <button v-if="currentUser?.role === 'seller'"
            @click="$router.push('/dashboard')">
      Dashboard
    </button>

    <button class="cart-btn" @click="$router.push('/cart')">
      <img src="/cart.png" alt="cart">
    </button>
  </div>

  <button class="logout" @click="logout">Logout</button>

</header>

    <div class="container">

  <h2>Request Order</h2>

  <!-- ITEMS -->
  <div v-for="item in cart" :key="item.id" class="card">
    <div class="card-content">
      <h3>{{ item.name }}</h3>
      <p class="price">₱{{ item.price }}</p>
    </div>
  </div>

  <!-- PREFERRED SCHEDULE -->
  <h3>Preferred Schedule</h3>

  <input type="date" v-model="date">

  <select v-model="timeRange">
    <option disabled value="">Select Time Range</option>
    <option>Morning (8AM–12PM)</option>
    <option>Afternoon (12PM–5PM)</option>
    <option>Evening (5PM–8PM)</option>
  </select>

  <input placeholder="Preferred Location" v-model="location">

  <!-- PAYMENT -->
  <h3>Payment</h3>
  <select v-model="payment">
    <option value="cod">Cash on Meetup</option>
    <option value="gcash">GCash</option>
  </select>

  <button @click="placeRequest">Send Request</button>

</div>

  </div>
</template>

<script>
export default {
data() {
  return {
    cart: JSON.parse(localStorage.getItem("cart")) || [],
    currentUser: JSON.parse(localStorage.getItem("currentUser")),
    date: "",
    timeRange: "",
    location: "",
    payment: "cod"
  };
},

methods: {
  placeRequest() {
    if (!this.date || !this.timeRange || !this.location) {
      alert("Complete schedule details");
      return;
    }

    const requests = JSON.parse(localStorage.getItem("requests")) || [];

    this.cart.forEach(item => {
      requests.push({
        id: Date.now(),
        product: item,
        buyer: this.currentUser.email,
        seller: item.owner,
        date: this.date,
        timeRange: this.timeRange,
        location: this.location,
        payment: this.payment,
        status: "pending"
      });
    });

    localStorage.setItem("requests", JSON.stringify(requests));
    localStorage.removeItem("cart");

    alert("Request sent! Waiting for seller approval.");
    this.$router.push("/");
  },

  logout() {
    localStorage.removeItem("currentUser");
    this.$router.push("/auth");
  }
}
};
</script>